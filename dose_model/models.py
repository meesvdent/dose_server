from django.db import models
from django.utils import timezone
from compounds.models import Compound
from django.contrib.auth.models import User


class Dose(models.Model):
    dose = models.FloatField()
    time = models.DateTimeField()
    duration = models.FloatField()
    mass = models.FloatField()
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def create_cur_model(self, doses, time, compound, mass, user, duration=60, calc_conc=True):
        self.dose = doses
        self.time = time
        self.duration = duration * 60
        self.mass = mass
        self.user = user
        self.save()

        compound_inst = Compound.objects.get(compound=compound)
        self.compound = compound_inst
        self.save(update_fields=['compound'])

        if calc_conc:
            self.calc_conc_model()

        return self

    def calc_conc_model(self):
        time = self.time
        dose = self.dose

        cur_compound = Compound.objects.filter(compound=self.compound).select_subclasses()
        cur_compound = cur_compound.first()

        result = cur_compound.calc_conc(dose, self.mass, self.duration)
        t = result['t']
        X = result['X']

        # save plasma concentrations in PlasmaConcentrationModel, related to current DoseModel instance
        for j in range(X.shape[1]):
            for i in range(len(X)):
                conc = PlasmaConcentration(
                    dose=self,
                    comp=j,
                    time=(time + timezone.timedelta(seconds=t[i])),
                    conc=X[i, j])
                conc.save()

        return self


class PlasmaConcentration(models.Model):
    dose = models.ForeignKey(Dose, on_delete=models.CASCADE, related_name="plasma_conc", null=True)
    comp = models.IntegerField()
    time = models.DateTimeField()
    conc = models.FloatField()







