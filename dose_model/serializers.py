from rest_framework import serializers
from .models import CompoundType, Compound, ConcentrationModel

class CompoundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompoundType
        fields = ('type', 'description', 'upload_date')


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ('compound', 'compound_type', 'mol_mass', 't_half', 'k_abs', 'dv', 'description', 'upload_date')

class ConcentrationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcentrationModel
        fields = ('doses', 'time', 'mass', 'compound', 'conc')
