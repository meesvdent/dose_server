from django.shortcuts import render
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose, Compound, PlasmaConcentration


def get_compound_type(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CompoundSubsetForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            dose_type = form.cleaned_data['type']


def get_dose(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'btnform1' in request.POST:
            compound_type_form = CompoundSubsetForm(request.POST)
            if compound_type_form.is_valid():
                type_choice = compound_type_form.cleaned_data['compound_type']

                type_choice = list(type_choice)
                type_choice = [choice for choice in type_choice]

                compound_queryset = Compound.objects.filter(compound_type__in=type_choice)
                filtered_dose_form = DoseForm()
                filtered_dose_form.fields["compound"].queryset = compound_queryset
                concentration_form = PlasmaConcentrationForm()
                return render(
                    request, 'dose_form.html',
                    {'compound_type': compound_type_form, 'dose_form': filtered_dose_form, 'plasma_conc': concentration_form})
            else:
                print("not valid")

        elif 'btnform2' in request.POST:
            # create a form instance and populate it with data from the request:
            dose_form = DoseForm(request.POST)
            # dose_form['dose'].choices
            # check whether it's valid:
            if dose_form.is_valid():
                dose = dose_form.cleaned_data['dose']
                time = dose_form.cleaned_data['time']
                compound = dose_form.cleaned_data['compound']
                mass = dose_form.cleaned_data['mass']

                cur_model = Dose()
                cur_model.create_cur_model(doses=dose, time=time, compound=compound, mass=mass)
                cur_model.calc_conc_model()
                compound_type = CompoundSubsetForm()
                dose_form = DoseForm()
                plasma_form = PlasmaConcentrationForm()

                return render(request, 'dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': plasma_form})

        elif 'btnform3' in request.POST:
            print(request.POST)
            conc_form = PlasmaConcentrationForm(request.POST)
            if conc_form.is_valid():
                dose_choice = conc_form.cleaned_data['dose']
                return dose_chart(request, dose_choice)
            else:
                print("not valid")



        else:
            print("nothing in there")
            dose_form = DoseForm()
            compound_type = CompoundSubsetForm()
            return render(request, 'dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': PlasmaConcentrationForm})

    # if a GET (or any other method) we'll create a blank form
    else:
        dose_form = DoseForm()
        compound_type = CompoundSubsetForm()

        return render(request, 'dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': PlasmaConcentrationForm})


def dose_chart(request, ids):

    datasets = {}
    for an_id in ids:
        dose_query = Dose.objects.get(id=an_id)

        conc_query = PlasmaConcentration.objects.filter(dose=an_id)

        values = list(conc_query.values('time', 'conc'))
        for coord_dict in values:
            coord_dict['x'] = coord_dict.pop('time')
            coord_dict['y'] = coord_dict.pop('conc')


        print(dose_query.compound.color)
        datasets[an_id] = {'compound': str(dose_query.compound), 'color': str(dose_query.compound.color), 'value': values}
        print("datasets: ", datasets)



    return render(request, 'dose_chart.html', {
        'data': datasets
    })
