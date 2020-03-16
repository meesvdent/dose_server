from django.db import models
from django.utils import timezone

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
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.compound


