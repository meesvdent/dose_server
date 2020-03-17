from django.db import models
import numpy as np
from django.utils import timezone
from dose_model.dose_model.models import OneCompModel
import json
from .dose_model.helpers import calc_dose_conc, trans_thalf_ke

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
    compound_type = models.ManyToManyField(CompoundType)
    description = models.TextField()
    photo = models.ImageField(upload_to="dose_server/dose_model/static/dose_model/structure_images/", null=True, blank=True)
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.compound


class ConcentrationModel(models.Model):
    doses = models.CharField(max_length=24*3600*100)
    time = models.CharField(max_length=24*3600*100)
    mass = models.FloatField()
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE, null=True)
    conc = models.CharField(max_length=24*3600*100)

    def create_cur_model(self, doses, time, compound, mass):
        self.doses = json.dumps(doses)
        self.time = json.dumps(time)
        self.mass = mass
        self.save()

        compound_inst = Compound.objects.get(compound=compound)
        self.compound = compound_inst
        self.save()

        return self


    def calc_conc_model(self):
        t = np.linspace(0, 24 * 3600, 24 * 3600)
        time = self.time
        time = time.strip('][').split(', ')
        time = [float(tim) for tim in time]
        doses = self.doses
        doses = doses.strip('][').split(', ')
        doses = [float(dose) for dose in doses]
        print(doses)
        cur_compound = Compound.objects.get(compound=self.compound)
        dv = cur_compound.dv * self.mass

        dose_conc = calc_dose_conc(doses, float(cur_compound.mol_mass), float(dv))

        ke = trans_thalf_ke(cur_compound.t_half)

        time_conc = [list(a) for a in zip(time, dose_conc)]

        temp_model = OneCompModel(time_conc, ke, cur_compound.k_abs)
        amount_unabs = temp_model.calc_unabs(t)
        delta_abs = temp_model.delta_abs(amount_unabs)
        X, infodict = temp_model.integrate(t)
        self.conc = json.dumps(X.tolist())
        self.save()

        return self







