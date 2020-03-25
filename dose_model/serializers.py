from rest_framework import serializers
from .models import CompoundType, Compound, Dose, PlasmaConcentration


class CompoundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompoundType
        fields = ('type', 'description', 'upload_date')


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ('compound', 'compound_type', 'mol_mass', 't_half', 'k_abs', 'dv', 'description', 'upload_date')


class DoseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dose
        fields = ('dose', 'time', 'mass', 'compound')


class PlasmaConcentrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlasmaConcentration
        fields = ('dose', 'time', 'conc')


