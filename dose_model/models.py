from django.db import models
import numpy as np
from django.utils import timezone
from dose_model.kinetics_models import OneCompModel
from dose_model.helpers import calc_dose_conc, trans_thalf_ke


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
    compound = models.CharField(max_length=200)
    mol_mass = models.FloatField()
    t_half = models.FloatField()
    k_abs = models.FloatField()
    dv = models.FloatField()
    compound_type = models.ManyToManyField(CompoundType, related_name='compound')
    description = models.TextField()
    photo = models.ImageField(upload_to="./static/dose_model/structure_images/", null=True, blank=True)
    color = models.CharField(max_length=200)
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.compound


class Dose(models.Model):
    dose = models.FloatField()
    time = models.DateTimeField()
    mass = models.FloatField()
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE, null=True)
    #TODO: user/session

    def create_cur_model(self, doses, time, compound, mass):
        self.dose = doses
        self.time = time
        self.mass = mass
        self.save()

        compound_inst = Compound.objects.get(compound=compound)
        self.compound = compound_inst
        self.save(update_fields=['compound'])

        return self


    def calc_conc_model(self):

        time = self.time
        doses = self.dose

        cur_compound = Compound.objects.get(compound=self.compound)
        dv = float(cur_compound.dv * self.mass)

        # model for t-start until 6 * halflife: 0.015625 left
        halflife_m = round(cur_compound.t_half * 60) # rounded half life in minutes
        t = np.linspace(0, 10 * halflife_m * 60, 10 * halflife_m + 1)
        dose_conc = calc_dose_conc([doses], float(cur_compound.mol_mass), dv)
        ke = trans_thalf_ke(cur_compound.t_half * 3600)
        time_conc = [list(a) for a in zip([0], dose_conc)]
        temp_model = OneCompModel(time_conc, ke, cur_compound.k_abs)
        amount_unabs = temp_model.calc_unabs(t)
        delta_abs = temp_model.delta_abs(amount_unabs)
        X, infodict = temp_model.integrate(t)
        X = [number[0] for number in X]

        # save plasma concentrations in PlasmaConcentrationModel, related to current DoseModel instance
        for i in range(len(X)):
            conc = PlasmaConcentration(
                dose=self,
                time=(time + timezone.timedelta(seconds=t[i])),
                conc=X[i])
            conc.save()

        return self


class PlasmaConcentration(models.Model):
    dose = models.ForeignKey(Dose, on_delete=models.CASCADE, related_name="plasma_conc", null=True)
    time = models.DateTimeField()
    conc = models.FloatField()







