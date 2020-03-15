import subprocess
import pandas
import numpy as np
from django.http import HttpResponse
from dose_model.dose_model.helpers import calc_dose_conc, trans_thalf_ke

from dose_model.dose_model.models import OneCompModel

# Create your views here.
update_model_sh = '../dose_model/static/dose_model/update_model.sh'


def home(request):
    return HttpResponse("Welcome")


def update_model(request):
    subprocess.Popen([update_model_sh], shell=True)
    return HttpResponse("models.py updated!")


def calc_conc(request):

    t = np.linspace(0, 24 * 3600, 24 * 3600)

    compound = int(request.GET.get("compound"))
    dosestring = request.GET.get("dosage")  # grams, seconds
    dosestr = dosestring.replace(']', '').replace('[', '')
    dose = dosestr.replace('"', '').split(",")
    dose = list(map(float, dose))

    timestring = request.GET.get("time")
    timestr = timestring.replace(']', '').replace('[', '')
    time = timestr.replace('"', '').split(",")
    time = list(map(int, time))

    compounds = pandas.read_csv('./dose_model/dose_model/compounds.csv', sep=";", header=0)

    molecularMass = compounds.iloc[compound, 2]  # Caffeine

    patientMass = float(request.GET.get("weight")) # kg
    DV = compounds.iloc[compound, 1] * patientMass  # L/kg, for caffeine
    ke = trans_thalf_ke(compounds.iloc[compound, 3] * 3600)

    dose_conc = calc_dose_conc(dose, molecularMass, DV)
    time_conc = [list(a) for a in zip(time, dose_conc)]


    model = OneCompModel(time_conc, ke, compounds.iloc[compound, 4])
    amount_unabs = model.calc_unabs(t)
    delta_abs = model.delta_abs(amount_unabs)

    X, infodict = model.integrate(t)

    return HttpResponse(X)

