from django.shortcuts import render
from .forms import CompoundSubsetForm, DoseForm, PlasmaConcentrationForm
from dose_model.models import Dose
from compounds.models import Compound
from django.contrib import messages


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

                return render(request, 'plot_dose/dose_form.html', {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': conc_form})
            else:
                messages.error(request, "Invalid form")
                return render(request, 'plot_dose/dose_form.html',
                              {'compound_type': compound_type, 'dose_form': dose_form, 'plasma_conc': conc_form})
        elif 'btnform3' in request.POST:
            conc_form = PlasmaConcentrationForm(doses, request.POST)
            if conc_form.is_valid():
                dose_choice = conc_form.cleaned_data['dose']
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


def dose_chart_data(ids, output='standard_dose_unit'):
    compounds_dose = {}
    queryset = Dose.objects.filter(id__in=ids)

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

    if output == 'standard_dose_unit':
        doses = cur_compound.convert_units(doses, output)

    return doses


def test_chartjs_scroll(request):
    return render(request, 'plot_dose/chart-js_scroll.html')

