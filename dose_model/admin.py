from django.contrib import admin
from .models import Compound, CompoundType, ConcentrationModel

admin.site.register(Compound)
admin.site.register(CompoundType)
admin.site.register(ConcentrationModel)