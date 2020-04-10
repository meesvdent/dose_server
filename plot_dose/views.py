from django.shortcuts import render
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose, Compound, PlasmaConcentration
import numpy as np


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

                filtered_concentration_form = PlasmaConcentrationForm(request.session['doses'])

                return render(
                    request, 'plot_dose/dose_form.html',
                    {'compound_type': compound_type_form, 'dose_form': filtered_dose_form, 'plasma_conc': filtered_concentration_form})
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

                request.session['doses'].append(cur_model.id)
                request.session.modified = True

                filtered_concentration_form = PlasmaConcentrationForm(request.session['doses'])

                compound_type = CompoundSubsetForm()
                dose_form = DoseForm()
                return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': filtered_concentration_form})

        elif 'btnform3' in request.POST:
            conc_form = PlasmaConcentrationForm(request.session['doses'], request.POST, )
            if conc_form.is_valid():
                dose_choice = conc_form.cleaned_data['dose']
                return dose_chart(request, dose_choice)
            else:
                print("not valid")



        else:
            dose_form = DoseForm()
            compound_type = CompoundSubsetForm()
            filtered_concentration_form = PlasmaConcentrationForm(request.session['doses'])

            return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': filtered_concentration_form})

    # if a GET (or any other method) we'll create a blank form
    else:
        dose_form = DoseForm()
        compound_type = CompoundSubsetForm()
        if 'doses' not in request.session.keys():
            request.session['doses'] = []
        filtered_concentration_form = PlasmaConcentrationForm(request.session['doses'])
        return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': filtered_concentration_form})


def dose_chart(request, ids):

    doses = dose_chart_data(ids)

    filtered_concentration_form = PlasmaConcentrationForm(request.session['doses'])
    compound_type = CompoundSubsetForm()
    dose_form = DoseForm()

    return render(request, 'plot_dose/dose_chart.html', {
        'data': doses,
        'compound_type': compound_type,
        'dose_form': dose_form,
        'plasma_conc': filtered_concentration_form
    })


def dose_chart_data(ids):
    doses = {}

    for an_id in ids:
        dose_query = Dose.objects.get(id=an_id)

        conc_query = PlasmaConcentration.objects.filter(dose=an_id)

        coords = list(conc_query.values('time', 'conc'))
        for coord_dict in coords:
            coord_dict['x'] = coord_dict.pop('time')
            coord_dict['y'] = coord_dict.pop('conc')

        doses[an_id] = {
            'compound': str(dose_query.compound),
            'color': str(dose_query.compound.color),
            'line': [10, 10],
            'coords': coords}

    # Add up concentration from same compound at same tame (for same user)

    cumulative = {}
    for key, dose in doses.items():

        if dose['compound'] not in cumulative.keys():
            cumulative[dose['compound']] = {
                'compound': dose['compound'],
                'color': dose['color'],
                'line': [],
                'coords': []}

        i = 0
        for dose_coord_dict in dose['coords']:

            if dose_coord_dict['x'] not in [cumulative_coord_dict['x'] for cumulative_coord_dict in cumulative[dose['compound']]['coords']]:
                cumulative[dose['compound']]['coords'].append(dose_coord_dict)
                i = i+1
            else:
                i = [cumulative_coord_dict['x'] for cumulative_coord_dict in cumulative[dose['compound']]['coords']].index(dose_coord_dict['x'])
                cumulative_x = dose_coord_dict['x']
                cumulative_y = dose_coord_dict['y'] + cumulative[dose['compound']]['coords'][i]['y']
                cumulative_coord = {'x': cumulative_x, 'y': cumulative_y}
                cumulative[dose['compound']]['coords'][i] = cumulative_coord
                i = i+1

    doses.update(cumulative)
    return doses

