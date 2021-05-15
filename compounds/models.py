from django.db import models
from rdkit import Chem
from rdkit.Chem import Draw
from django.core.files import File
from dose_model.helpers import trans_thalf_ke, calc_dose_conc
from dose_model.kinetics_models import SourceOneCompFirstOrder, PietersModel
import numpy as np
from model_utils.managers import InheritanceManager
from django.utils import timezone
from math import log2
import dose_model.models as dose_model
from django.utils import timezone
import copy


class CompoundType(models.Model):
    type = models.CharField(max_length=200)
    description = models.TextField()
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.type


class Compound(models.Model):

    # all compounds properties
    compound = models.CharField(max_length=200)
    compound_type = models.ManyToManyField(CompoundType, related_name='compound')
    mol_mass = models.FloatField()
    dv = models.FloatField()
    n_comps = 1
    comp_of_interest = 1
    standard_dose = models.FloatField()
    standard_dose_max = models.FloatField(blank=True, null=True)
    clearance_types = [(str(i), ['Renal', 'Enzymatic'][i]) for i in range(2)]
    clearance_type = models.CharField(max_length=1, choices=clearance_types)

    # extra
    description = models.TextField()
    photo = models.ImageField(upload_to="compound_structures", null=True, blank=True)
    color = models.CharField(max_length=200)
    smiles = models.CharField(max_length=2000, null=True)
    upload_date = models.DateTimeField(blank=True, null=True)

    objects = InheritanceManager()

    def convert_units(self, doses, output='standard_dose_unit'):
        if output == 'mol/L':
            return doses
        else:
            new_doses = copy.deepcopy(doses)
            for key, value in doses.items():
                print(key)
                # for key, value in doses.items():
                #     print(key)
                #     y_1 = list([coord['y'] for coord in doses[key]['coords']])
                #     print(max(y_1))

                compound = Compound.objects.filter(compound=value['compound']).select_subclasses().first()
                if output == 'standard_dose_unit':

                    for i in range(len(value['coords'])):
                        new_doses[key]['coords'][i]['y'] = float(value['coords'][i]['y']) / compound.standard_dose_max
        return new_doses

    def add_doses_first_order(self, doses, cumulative):
        """
        Adds each dose up to the cumulative dose.

        :param doses: dict
        :param cumulative: dict
        :return: dict

        TODO: optimize with numpy, this is horribly slow
        check range function (looks at first and last time of eacht dose
        create linspace for each minute in range and zeros

        add each dose to that array, match by date
        """
        for key, dose in doses.items():
            i = 0
            for dose_coord_dict in dose['coords']:
                if cumulative[dose['compound']]['first_date'] is None:
                    cumulative[dose['compound']]['first_date'] = dose_coord_dict['x']
                    cumulative[dose['compound']]['last_date'] = dose_coord_dict['x']
                if dose_coord_dict['x'] < cumulative[dose['compound']]['first_date']:
                    cumulative[dose['compound']]['first_date'] = dose_coord_dict['x']
                if dose_coord_dict['x'] > cumulative[dose['compound']]['last_date']:
                    cumulative[dose['compound']]['last_date'] = dose_coord_dict['x']
                if dose_coord_dict['x'] not in [cumulative_coord_dict['x'] for cumulative_coord_dict in
                                                cumulative[dose['compound']]['coords']]:
                    cumulative[dose['compound']]['coords'].append(dose_coord_dict)
                    i = i + 1
                else:
                    i = [cumulative_coord_dict['x'] for cumulative_coord_dict in
                         cumulative[dose['compound']]['coords']].index(dose_coord_dict['x'])
                    cumulative_x = dose_coord_dict['x']
                    cumulative_y = dose_coord_dict['y'] + cumulative[dose['compound']]['coords'][i]['y']
                    cumulative_coord = {'x': cumulative_x, 'y': cumulative_y}
                    cumulative[dose['compound']]['coords'][i] = cumulative_coord
                    i = i + 1

        return cumulative

    def add_doses_recalc(self, doses, cumulative_coords, X0, ncomps, comp_of_int, startzero=True):
        keys = list(doses.keys())
        if len(keys) == 0:
            return cumulative_coords

        compound = Compound.objects.filter(compound=doses[keys[0]]['compound']).select_subclasses().first()
        cur_dose = dose_model.Dose.objects.get(id=keys[0])

        if len(keys) == 1:  # last dose
            if startzero:  # add last dose from memory
                cumulative_coords = cumulative_coords + doses[keys[0]]['coords']
                del doses[keys[0]]
                X0 = [0 for i in range(self.n_comps)]
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, comp_of_int=comp_of_int)
                return cumulative_coords
            else:  # calculate last dose with calculated X0 and add it
                time_range = compound.calc_time_range_min(dose=cur_dose.dose, duration=cur_dose.duration, X0=X0)
                new_dict = compound.calc_conc(
                    dose=cur_dose.dose,
                    mass=cur_dose.mass,
                    duration=cur_dose.duration,
                    X0=X0,
                    time_range=time_range)
                new_conc = new_dict['X'][:, comp_of_int]
                new_times = new_dict['t']
                new_coords = []
                for i in range(len(new_conc)):
                    new_coords.append({
                        'x': cur_dose.time + timezone.timedelta(seconds=new_times[i]),
                        'y': new_conc[i]
                    })
                cumulative_coords = cumulative_coords + new_coords

                del doses[keys[0]]
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, startzero=True, comp_of_int=comp_of_int)
                return cumulative_coords

        next_dose = dose_model.Dose.objects.get(id=keys[1])
        if startzero:
            last_current = doses[keys[0]]['coords'][-1]['x']
        else:
            time_range = compound.calc_time_range_min(dose=cur_dose.dose, duration=cur_dose.duration, X0=X0)
            last_current = cur_dose.time + timezone.timedelta(minutes=time_range)

        first_next = doses[keys[1]]['coords'][0]['x']
        first_current = doses[keys[0]]['coords'][0]['x']
        dt = int((first_next - first_current).seconds/60)

        if first_next > last_current:  # there is no overlap with next
            if startzero:  # just add the coords already in memory
                cumulative_coords = cumulative_coords + doses[keys[0]]['coords']
                del doses[keys[0]]
                X0 = [0 for i in range(self.n_comps)]
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, comp_of_int=comp_of_int)
                return cumulative_coords
            else:  # recalc the coords from new X0
                time_range = compound.calc_time_range_min(dose=cur_dose.dose, duration=cur_dose.duration, X0=X0)
                new_dict = compound.calc_conc(
                    dose=cur_dose.dose,
                    mass=cur_dose.mass,
                    duration=cur_dose.duration,
                    X0=X0,
                    time_range=time_range)
                new_conc = new_dict['X'][:, comp_of_int]
                new_times = new_dict['t']
                new_coords = []
                for i in range(len(new_conc)):
                    new_coords.append({
                        'x': cur_dose.time + timezone.timedelta(seconds=new_times[i]),
                        'y': new_conc[i]
                    })
                cumulative_coords = cumulative_coords + new_coords

                del doses[keys[0]]
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, startzero=True,
                                                          comp_of_int=comp_of_int)
                return cumulative_coords
        else:  # there is overlap with the next dose
            if startzero:  # add everything untill the next dose and resubmit with startzero is false and proper X0
                cumulative_coords = cumulative_coords + doses[keys[0]]['coords'][0:dt]
                X0 = []
                for i in range(ncomps):
                    X0_queryset = dose_model.PlasmaConcentration.objects.filter(dose=keys[0], comp=i, time=first_next)
                    print(first_next)
                    X0_values = X0_queryset.values_list('conc', flat=True)[0]
                    X0.append(X0_values)
                del doses[keys[0]]
                print(X0)
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, comp_of_int=comp_of_int, startzero=False)
                return cumulative_coords
            else:
                # recalculate everything with proper X0 untill the next dose
                # resubmit with startzero is false and proper X0
                new_dict = compound.calc_conc(
                    dose=cur_dose.dose,
                    mass=cur_dose.mass,
                    duration=cur_dose.duration,
                    X0=X0,
                    time_range=dt)
                new_conc = new_dict['X'][:, comp_of_int]
                new_times = new_dict['t']
                new_coords = []
                for i in range(len(new_conc)):
                    new_coords.append({
                        'x': cur_dose.time + timezone.timedelta(seconds=new_times[i]),
                        'y': new_conc[i]
                    })
                cumulative_coords = cumulative_coords + new_coords

                # make new X0:
                X0 = []
                for i in range(ncomps):
                    X0.append(new_dict['X'][-1, i])
                del doses[keys[0]]
                cumulative_coords = self.add_doses_recalc(doses, cumulative_coords, X0, ncomps=ncomps, startzero=False,
                                                          comp_of_int=comp_of_int)
                return cumulative_coords

    def calc_overlap_dose(self, dose_list, doses, compound):
        """
        When the ingestion of two doses overlap, a virtual dose has to be calculated where the first part consists
        of the first and second dose added together, followed by the part of the second dose which is given on its own.
        :param doses: array of ints
        :return:
        """
        if(len(doses)) == 1:
            return dose_list, doses

        cur_compound = Compound.objects.filter(compound=compound).select_subclasses().first()

        i = 0
        keys = list(doses.keys())
        while i < (len(keys) - 1):
            print('keys: ', keys)

            cur_dose = dose_model.Dose.objects.get(id=keys[i])
            next_dose = dose_model.Dose.objects.get(id=keys[i+1])

            first_next = doses[keys[i+1]]['coords'][0]['x']
            first_current = doses[keys[i]]['coords'][0]['x']
            dt = int((first_next - first_current).seconds/60)

            print('dt: ', dt)

            if dt < cur_dose.duration/60:
                if cur_dose.duration == 0:
                    cur_dose.duration = 1
                first_dose_per_minute = cur_dose.dose / (cur_dose.duration/60)
                if next_dose.duration == 0:
                    next_dose.duration = 1

                second_dose_per_minute = next_dose.dose / (next_dose.duration/60)

                if cur_dose.duration/60 < dt + next_dose.duration/60:
                    overlap = cur_dose.duration / 60 - dt
                    first_dose_overlap = first_dose_per_minute * overlap
                    if cur_dose.duration == 0:
                        first_dose_overlap = cur_dose.dose
                    first_dose = first_dose_per_minute * (cur_dose.duration / 60 - overlap)
                    second_dose_overlap = second_dose_per_minute * overlap
                    if next_dose.duration == 0:
                        second_dose_overlap = next_dose.dose
                    second_dose = second_dose_per_minute * (next_dose.duration/60 - overlap)
                    second_dose_duration = next_dose.duration/60 - overlap
                elif cur_dose.duration/60 >= dt + next_dose.duration/60:
                    overlap = next_dose.duration / 60
                    first_dose_overlap = first_dose_per_minute * overlap
                    if cur_dose.duration == 0:
                        first_dose_overlap = cur_dose.dose
                    first_dose = first_dose_per_minute * dt
                    second_dose_overlap = second_dose_per_minute * overlap
                    if next_dose.duration == 0:
                        second_dose_overlap = next_dose.dose
                    second_dose = first_dose_per_minute * (cur_dose.duration/60 - overlap - dt)
                    second_dose_duration = cur_dose.duration/60 - overlap - dt

                overlap_dose = first_dose_overlap + second_dose_overlap
                doses_amount = [first_dose, overlap_dose, second_dose]
                times = [cur_dose.time, next_dose.time, cur_dose.time + timezone.timedelta(minutes=(dt+1)) + timezone.timedelta(minutes=overlap)]
                durations = [dt, overlap, second_dose_duration]

                print('new doses: ', doses_amount, times, durations)

                overlap_doses = []
                add_count = 0
                for j in range(3):
                    if doses_amount[j] != 0:
                        cur_model = dose_model.Dose()
                        cur_model.create_cur_model(
                            doses=doses_amount[j],
                            time=times[j],
                            compound=cur_dose.compound,
                            mass=cur_dose.mass,
                            user=None,
                            duration=durations[j]
                        )
                        overlap_doses.append(cur_model.id)
                        print(doses_amount[j])
                        print(durations[j])
                        add_count += 1

                dose_list[i:i+2] = overlap_doses
                print('dose_list: ', dose_list)
                doses, cumulative = cur_compound.dose_chart_data(dose_list, comp_of_interest=cur_compound.comp_of_interest)
                keys = list(doses.keys())
                dose_list = keys
                print(keys)
                print('i', i)
                print('len(keys)-1', len(keys) -1)

            else:
                i += 1

        return dose_list, doses

    def __str__(self):
        return self.compound

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.smiles and not self.photo:
            url = draw_compound_structure(smiles=self.smiles, name=self.compound, width=300, height=300)

            self.photo.save(self.compound+".png", File(open(url, 'rb')))

        if not self.standard_dose_max:
            cur_compound = Compound.objects.filter(compound=self.compound).select_subclasses()
            cur_compound = cur_compound.first()

            result = cur_compound.calc_conc(self.standard_dose, 75, 0)
            X = result['X']
            self.standard_dose_max = max(X[:, self.comp_of_interest])
            self.save()


class OneCompFirstOrderCompound(Compound):

    k_abs_one_comp = models.FloatField(null=True, blank=True)
    t_half_in_hours = models.FloatField(null=True, blank=True)

    n_comps = 2
    comp_of_interest = 1

    def calc_conc(self, dose, mass, duration, X0=[0, 0]):
        # model for t-start until 6 * halflife: 0.015625 left
        halflife_m = round(self.t_half_in_hours * 60)  # rounded half life in minutes
        t = np.linspace(0, 10 * halflife_m * 60, 10 * halflife_m + 1)

        ke = trans_thalf_ke(self.t_half_in_hours * 3600)
        dv = mass * self.dv

        dose_conc = calc_dose_conc([dose], float(self.mol_mass), dv)
        dose = [list(a) for a in zip(dose_conc, [0], [duration])]
        model = SourceOneCompFirstOrder(X0=X0, doses=dose, k_s1=self.k_abs_one_comp, k_ex=ke)

        X = model.integrate(t)

        return {'t': t, 'X': X}

    def calc_cumulative(self, doses, cumulative):
        cumulative = self.add_doses_first_order(doses, cumulative)
        return cumulative

    def check_overlap(self, doses, dose_dicts, compound):
        return doses, dose_dicts


class PietersModelCompound(Compound):
    # Enzymatic metabolisation parameters
    v_max = models.FloatField(null=True, blank=True)
    k_m = models.FloatField(null=True, blank=True)

    # Pieters model uptake
    k_12 = models.FloatField(null=True, blank=True)
    k_23 = models.FloatField(null=True, blank=True)
    a_av = models.FloatField(null=True, blank=True)

    n_comps = 3
    comp_of_interest = 2  # the third compartment

    def calc_time_range_min(self, dose, duration, X0):
        dur_min = round(log2(((dose + sum(X0)) * 1E100) + duration / 60))
        return dur_min

    def calc_conc(self, dose, mass, duration, X0=[0, 0, 0], time_range=None):
        if time_range is None:
            time_range = self.calc_time_range_min(dose, duration, X0)

        dv = mass * self.dv
        dose_conc = calc_dose_conc([dose], float(self.mol_mass), dv)
        dose = [list(a) for a in zip(dose_conc, [0], [duration])]

        model = PietersModel(X0=X0, doses=dose, k12=self.k_12, k23=self.k_23, vmax=self.v_max, km=self.k_m, a=self.a_av)

        t = np.linspace(0, time_range * 60, time_range + 1)
        X = model.integrate(t)

        return {'t': t, 'X': X}

    def calc_cumulative(self, doses, cumulative):
        cumulative_coords = []
        X0 = [0 for i in range(self.n_comps)]
        cumulative_coords = self.add_doses_recalc(
            doses,
            cumulative_coords,
            X0=X0,
            ncomps=self.n_comps,
            comp_of_int=self.comp_of_interest)
        keys = list(cumulative.keys())
        cumulative[keys[0]]['coords'] = cumulative_coords
        return cumulative

    def check_overlap(self, doses, dose_dicts, compound):
        return self.calc_overlap_dose(doses, dose_dicts, compound)


def draw_compound_structure(smiles, name, width, height):
    mol = Chem.MolFromSmiles(smiles)

    path = "media/compound_structures/" + name + ".png"
    Draw.MolToFile(mol, path, size=(width, height))
    return path


