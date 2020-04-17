from django.shortcuts import render, redirect
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose, PlasmaConcentration
from compounds.models import Compound
from django.contrib import messages
import datetime
from django.utils import timezone


def get_compound_type(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CompoundSubsetForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            dose_type = form.cleaned_data['type']


def get_dose(request):

    # prep empty forms
    if 'doses' not in request.session.keys():
        request.session['doses'] = []

    compound_type = CompoundSubsetForm()
    dose_form = DoseForm()

    if request.user.is_authenticated:
        doses_queryset = Dose.objects.filter(user__in=[request.user.id])
        doses_ids = doses_queryset.values_list('id', flat=True)
        doses = list(doses_ids)
    else:
        doses = request.session['doses']

    conc_form = PlasmaConcentrationForm(doses)

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

                return render(
                    request, 'plot_dose/dose_form.html',
                    {'compound_type': compound_type_form, 'dose_form': filtered_dose_form, 'plasma_conc': conc_form})
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
                if request.user.is_authenticated:
                    user = request.user
                else:
                    user = None

                cur_model.create_cur_model(doses=dose, time=time, compound=compound, mass=mass, user=user)

                request.session['doses'].append(cur_model.id)
                request.session.modified = True

                doses.append(cur_model.id)
                conc_form = PlasmaConcentrationForm(doses)

                return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': conc_form})

        elif 'btnform3' in request.POST:
            conc_form = PlasmaConcentrationForm(doses, request.POST)
            if conc_form.is_valid():
                dose_choice = conc_form.cleaned_data['dose']
                print(dose_choice)
                return dose_chart(request, dose_choice, conc_form)
            else:
                messages.error(request, "Add a dose to plot")
                return render(request, 'plot_dose/dose_form.html',
                              {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': conc_form})

        else:
            return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': conc_form})

    # if a GET (or any other method) we'll create a blank form
    else:
        return render(
            request,
            'plot_dose/dose_form.html',
            {
                'compound_type': compound_type,
                'dose_form': dose_form,
                'plasma_conc': conc_form
            }
        )


def dose_chart(request, ids, conc_form):

    doses = dose_chart_data(ids)

    # prep empty forms
    if 'doses' not in request.session.keys():
        request.session['doses'] = []
    filtered_concentration_form = conc_form
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
                'coords': [],
                'first_date': timezone.now(),
                'last_date': timezone.now()
            }

        i = 0
        for dose_coord_dict in dose['coords']:
            if dose_coord_dict['x'] < cumulative[dose['compound']]['first_date']:
                cumulative[dose['compound']]['first_date'] = dose_coord_dict['x']
            if dose_coord_dict['x'] > cumulative[dose['compound']]['last_date']:
                cumulative[dose['compound']]['last_date'] = dose_coord_dict['x']
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

    # # add zero values to empty dates in range and make minimal range 0-1 month
    # for key, dose in cumulative.items():
    #     dose['coords'] = sorted(dose['coords'], key = lambda k: k["x"])
    #     days = (dose['last_date'] - dose['first_date']).total_seconds()/(3600*24)
    #     days_difference = int(31 - days)
    #     print(days_difference)
    #
    #     if days_difference > 0:
    #         print(range(days_difference*24*3600))
    #         add_dates = dose['first_date'] - datetime.timedelta(seconds=days_difference*24*3600)
    #         print(add_dates)
    #         dose['coords'] = [{'x': add_dates, 'y': 0}] + dose['coords']
    #         print('added')

    doses.update(cumulative)
    return doses


def test_chartjs_scroll(request):
    return render(request, 'plot_dose/chart-js_scroll.html')

