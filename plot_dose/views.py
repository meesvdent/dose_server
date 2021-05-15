from django.shortcuts import render
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose, PlasmaConcentration
from compounds.models import Compound
from django.contrib import messages

import time


def get_compound_type(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CompoundSubsetForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            dose_type = form.cleaned_data['type']


def index(request):
    if 'doselist' not in request.session.keys():
        request.session['doselist'] = []

    if request.user.is_authenticated:
        doses_queryset = Dose.objects.filter(user__in=[request.user.id])
        doses_ids = doses_queryset.values_list('id', flat=True)
        request.session['doselist'] = list(doses_ids)


    if 'cumulative_doses' not in request.session.keys():
        update_doses()

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        if 'btnform2' in request.POST:
            # create a form instance and populate it with data from the request:
            dose_form = DoseForm(request.POST)
            # dose_form['dose'].choices
            # check whether it's valid:
            if dose_form.is_valid():
                messages.success(request, message="Adding your dose")
                dose = dose_form.cleaned_data['dose']
                time = dose_form.cleaned_data['time']
                duration = dose_form.cleaned_data['duration']
                compound = dose_form.cleaned_data['compound']
                mass = dose_form.cleaned_data['mass']

                cur_model = Dose()
                if request.user.is_authenticated:
                    user = request.user
                else:
                    user = None

                cur_model.create_cur_model(doses=dose, time=time, compound=compound, mass=mass, user=user, duration=duration)

                request.session['doses'].append(cur_model.id)
                request.session.modified = True

                doses.append(cur_model.id)
                request = update_chart_data(request)

            else:
                messages.error(request, "Invalid form")

    return dose_chart(request)


def dose_chart(request, conc_form):
    # prep empty forms
    if 'doses' not in request.session.keys():
        request.session['doses'] = []
    filtered_concentration_form = conc_form
    compound_type = CompoundSubsetForm()
    dose_form = DoseForm()

    return render(request, 'plot_dose/dose_chart.html', {
        'data': chart_data_dict,
        'compound_type': compound_type,
        'dose_form': dose_form,
        'plasma_conc': filtered_concentration_form
    })


def update_doses(request, add_doses=None, output='standard_dose_unit'):
    doselist = request.session['doselist']
    if 'cumulative_doses' not in request.session.keys():
        cumulative_doses = {}
        add_doses = list(doselist)
    else:
        cumulative_doses = request.session['cumulative_doses']


    queryset = Dose.objects.filter(id__in=doselist)
    for dose in queryset:
        if str(dose.compound) not in cumulative_doses.keys():
            cumulative_doses[str(dose.compound)] = {
                'single_doses' : [dose.id],
                'cumulative_dose': None,
                'updated': True
            }
        else:
            cumulative_doses[str(dose.compound)]['single_doses'].append(dose.id)
            cumulative_doses[str(dose.compound)]['updated'] = True

    for key, value in cumulative_doses.items():
        if value['updated']:
            cur_compound = Compound.objects.filter(compound=key).select_subclasses().first()
            comp_of_interest = cur_compound.comp_of_interest
            new_list, unusable_doses = cur_compound.check_overlap(value, cur_compound_doses, key)
            cumulative_doses = cur_compound.calc_cumulative(unusable_doses, cumulative)
            doses.update(cumulative_doses)
    if len(doses.keys()) > 0:
        if output == 'standard_dose_unit':
            doses = cur_compound.convert_units(doses, output)

    return request







def create_chart_data(self, id):
    # make a dict containing compound, color, line and coords
    dose_query = Dose.objects.get(id=id)
    compound = str(dose_query.compound)
    cur_compound = Compound.objects.filter(compound=compound).select_subclasses().first()
    comp_of_interest = cur_compound.comp_of_interest
    conc_query = PlasmaConcentration.objects.filter(dose=id, comp=comp_of_interest)

    coords = list(conc_query.values('time', 'conc'))
    for coord_dict in coords:
        coord_dict['x'] = coord_dict.pop('time')
        coord_dict['y'] = coord_dict.pop('conc')

    chart_data = {
        'compound': str(dose_query.compound),
        'color': str(dose_query.compound.color),
        'line': [10, 10],
        'coords': coords}

    return chart_data


def create_cumulative_chart_data:
    cumulative = {}
    for key, dose in doses.items():

        if dose['compound'] not in cumulative.keys():
            cumulative[dose['compound']] = {
                'compound': dose['compound'],
                'color': dose['color'],
                'line': [],
                'coords': [],
                'first_date': None,
                'last_date': None
            }

def update_dose_chart_data(dose_chart_data, id):



