from rest_framework import serializers
from .models import CompoundType, Compound, Dose, PlasmaConcentration



class CompoundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompoundType
        fields = ('type', 'description', 'upload_date')


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ('id', 'compound', 'compound_type', 'mol_mass', 't_half', 'k_abs', 'dv', 'description', 'upload_date')


class DoseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dose
        fields = ('id', 'dose', 'time', 'mass', 'compound')

    def create(self, validated_data):
        cur_dose = Dose.objects.create(**validated_data)
        cur_dose.calc_conc_model()
        return cur_dose

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.calc_conc_model()


class PlasmaConcentrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlasmaConcentration
        fields = ('dose', 'time', 'conc')

