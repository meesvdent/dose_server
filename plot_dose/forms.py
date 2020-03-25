from django.forms import ModelForm, MultipleChoiceField, Form, Select
from django.forms.widgets import CheckboxSelectMultiple, DateTimeInput
from dose_model.models import Compound, Dose, PlasmaConcentration


class CompoundSubsetForm(ModelForm):
    class Meta:
        model = Compound
        fields = ['compound_type']


class DoseForm(ModelForm):

    class Meta:
        model = Dose
        fields = ['compound', 'dose', 'time', 'mass']
        widgets = {
            'time': DateTimeInput()
        }


class PlasmaConcentrationForm(Form):
    def __init__(self, *args, **kwargs):
        super(PlasmaConcentrationForm, self).__init__(*args, **kwargs)
        self.iquery = Dose.objects.values('id', 'compound', 'time')

        self.iquery_choices = []
        for i in range(len(self.iquery)):
            choice = self.iquery[i]
            compound = Compound.objects.get(id=choice['compound']).compound
            self.iquery_choices.append((choice['id'], compound + " " + choice['time'].strftime("%m/%d/%Y, %H:%M:%S")))

        self.fields['dose'].choices = self.iquery_choices

    dose = MultipleChoiceField(
        choices=(),
        widget=CheckboxSelectMultiple,

    )







