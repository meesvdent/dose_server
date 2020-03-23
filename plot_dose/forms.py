from django.forms import ModelForm
from dose_model.models import CompoundType, ConcentrationModel

# class DoseTypeForm(ModelForm):
#     class Meta:
#         model = CompoundType
#         fields =
#     # compound_type_choice = forms.ModelChoiceField(
#     #     label="Type of compound",
#     #     queryset=CompoundType.objects.all(),
#     #     initial=0)


class DoseForm(ModelForm):
    class Meta:
        model = ConcentrationModel
        fields = ['compound', 'doses', 'time', 'mass']
    # def __init__(self):
    #     #self.compound_type = 0
    #     self.compound_choice = forms.ModelChoiceField(
    #         label="Compound",
    #         queryset=Compound.objects.all())
    #     self.mass_choice = forms.FloatField(label="Body weight (kg)", min_value=0, max_value=500)
    #     self.dose_choice = forms.FloatField(label="Dosage (g)", min_value=0)
    #     self.time_choice = forms.IntegerField(label="Ingestion time (sec)", min_value=0, max_value=24 * 3600)

    # compound_choice = forms.ModelChoiceField(
    #     label="Compound",
    #     queryset=Compound.objects.all())
    # mass_choice = forms.FloatField(label="Body weight (kg)", min_value=0, max_value=500)
    # dose_choice = forms.FloatField(label="Dosage (g)", min_value=0)
    # time_choice = forms.IntegerField(label="Ingestion time (sec)", min_value=0, max_value=24 * 3600)




