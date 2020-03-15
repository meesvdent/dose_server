from django.shortcuts import render
import subprocess
import numpy as np
from django.http import HttpResponse
from dose_model.dose_model.models import OneCompModel
from dose_model.dose_model.helpers import calc_dose_conc, trans_thalf_ke


# Create your views here.
update_model_sh = '../dose_model/static/dose_model/update_model.sh'


def home(request):
    return HttpResponse("Welcome")


def update_model(request):
    subprocess.Popen([update_model_sh], shell=True)
    return HttpResponse("models.py updated!")


def calc_conc(request):
    t = np.linspace(0, 24 * 3600, 24 * 3600)

    dose = [0.160, 0.160]  # grams, seconds
    time = [0.001, 7200]
    molecularMass = 194.19  # Caffeine

    patientMass = 75  # kg
    DV = 0.625 * patientMass  # L/kg, for caffeine
    ke = trans_thalf_ke(4 * 3600)
    print(ke)

    dose_conc = calc_dose_conc(dose, molecularMass, DV)
    time_conc = [list(a) for a in zip(time, dose_conc)]

    print(list(time_conc))

    model = OneCompModel(time_conc, ke, 0.0055)
    amount_unabs = model.calc_unabs(t)
    delta_abs = model.delta_abs(amount_unabs)

    X, infodict = model.integrate(t)

    return HttpResponse(X)

