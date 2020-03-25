from django.contrib import admin
from .models import Compound, CompoundType, Dose, PlasmaConcentration

admin.site.register(Compound)
admin.site.register(CompoundType)
admin.site.register(Dose)
admin.site.register(PlasmaConcentration)