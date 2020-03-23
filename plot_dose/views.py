from django.shortcuts import render
from .forms import DoseForm
from dose_model.models import ConcentrationModel
import json


def dose_chart(request, conc, time, compound):

    labels = time
    data = json.loads(conc)

    print(labels)
    print(data)
    print(str(compound))

    return render(request, 'dose_chart.html', {
        'labels': labels,
        'data': data,
        'compound': [str(compound)],
    })


def get_dose(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DoseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            dose = form.cleaned_data['doses']
            time = form.cleaned_data['time']
            compound = form.cleaned_data['compound']
            print("get dose compound: ", compound)
            mass = form.cleaned_data['mass']

            cur_model = ConcentrationModel()
            cur_model = cur_model.create_cur_model(doses=dose, time=time, compound=compound, mass=mass)
            cur_model = cur_model.calc_conc_model()


            return dose_chart(
                request,
                conc=cur_model.conc,
                time=[moment.strftime('%H:%M:%S') for moment in cur_model.time_field],
                compound=cur_model.compound)


    # if a GET (or any other method) we'll create a blank form
    else:
        form = DoseForm()

    return render(request, 'dose_form.html', {'form': form})



