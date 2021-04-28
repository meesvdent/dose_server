from django.shortcuts import render
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose
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

    # prep empty forms
    if 'doses' not in request.session.keys():
        request.session['doses'] = []

    if request.user.is_authenticated:
        doses_queryset = Dose.objects.filter(user__in=[request.user.id])
        doses_ids = doses_queryset.values_list('id', flat=True)
        doses = list(doses_ids)
    else:
        doses = request.session['doses']

    conc_form = PlasmaConcentrationForm(doses)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        if 'btnform2' in request.POST:
            # create a form instance and populate it with data from the request:
            dose_form = DoseForm(request.POST)
            # dose_form['dose'].choices
            # check whether it's valid:
            if dose_form.is_valid():
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
                conc_form = PlasmaConcentrationForm(doses)

            else:
                messages.error(request, "Invalid form")

    return dose_chart(request, doses, conc_form)


def dose_chart(request, ids, conc_form):
    begin = time.time()
    doses = dose_chart_data(ids)
    end = time.time()

    print(end-begin)

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


def dose_chart_data(ids, output='standard_dose_unit'):
    compounds_dose = {}

    queryset = Dose.objects.filter(id__in=ids)
    begin = time.time()
    for dose in queryset:
        if str(dose.compound) not in compounds_dose.keys():
            compounds_dose[str(dose.compound)] = [dose.id]
        else:
            compounds_dose[str(dose.compound)].append(dose.id)

    doses = {}
    for key, value in compounds_dose.items():
        cur_compound = Compound.objects.filter(compound=key).select_subclasses().first()
        comp_of_interest = cur_compound.comp_of_interest
        cur_compound_doses, cumulative = cur_compound.dose_chart_data(value, comp_of_interest=comp_of_interest)
        doses.update(cur_compound_doses)
        new_list, unusable_doses = cur_compound.check_overlap(value, cur_compound_doses, key)
        cumulative_doses = cur_compound.calc_cumulative(unusable_doses, cumulative)
        doses.update(cumulative_doses)
    if len(doses.keys()) > 0:
        if output == 'standard_dose_unit':
            doses = cur_compound.convert_units(doses, output)

    return doses



