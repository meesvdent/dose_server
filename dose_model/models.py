from django.db import models
from django.utils import timezone


class Compound(models.Model):
    compound = models.CharField(max_length=200)
    mol_mass = models.FloatField()
    t_half = models.FloatField()
    k_abs = models.FloatField()
    dv = models.FloatField()

    # define types of compounds
    focus = 'foc'
    power = 'pow'
    type_choices = (
        (focus, 'Focus'),
        (power, 'Power')
    )
    compound_type = models.CharField(max_length=3, choices=type_choices, default=focus)

    description = models.TextField()
    upload_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.upload_date = timezone.now()
        self.save()

    def __str__(self):
        return self.compound

