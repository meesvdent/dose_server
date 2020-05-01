from django.contrib import admin
from .models import Dose, PlasmaConcentration
from compounds.models import CompoundType, Compound


admin.site.register(Compound)
admin.site.register(CompoundType)
admin.site.register(Dose)
admin.site.register(PlasmaConcentration)


