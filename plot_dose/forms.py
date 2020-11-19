from django.forms import ModelForm, MultipleChoiceField, Form, Select
from bootstrap_datepicker_plus import DateTimePickerInput
from django.forms.widgets import CheckboxSelectMultiple, DateTimeInput
from dose_model.models import Dose, PlasmaConcentration
from compounds.models import Compound


class CompoundSubsetForm(ModelForm):
    class Meta:
        model = Compound
        fields = ['compound_type']
        labels = {
            'compound_type': 'Compound type'
        }


class DoseForm(ModelForm):
    class Meta:
        model = Dose
        fields = ['compound', 'dose', 'time', 'duration', 'mass']
        widgets = {
            'time': DateTimePickerInput(),
        }
        labels = {
            'compound': 'Compound',
            'dose': 'Dose (grams)',
            'mass': 'Bodyweight',
            'time': 'Date and time',
            'duration': 'Duration (minutes)'
        }


class PlasmaConcentrationForm(Form):
    def __init__(self, ids, *args, **kwargs):
        super(PlasmaConcentrationForm, self).__init__(*args, **kwargs)
        self.iquery = Dose.objects.filter(id__in=ids)
        self.iquery = self.iquery.values('id', 'compound', 'time')

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

    class Meta:
        labels = {
            'dose': '',
        }







