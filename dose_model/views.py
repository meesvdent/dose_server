import subprocess
import numpy as np
from django.http import HttpResponse
from dose_model.dose_model.helpers import calc_dose_conc, trans_thalf_ke
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CompoundSerializer
from .models import Compound


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

    cur_comp = Compound.objects.get(compound='Caffeine')

    molecular_mass = cur_comp.mol_mass  # Caffeine

    patient_mass = float(request.GET.get("weight"))  # kg
    print(cur_comp.dv)
    DV = cur_comp.dv * patient_mass  # L/kg, for caffeine
    ke = trans_thalf_ke(cur_comp.t_half * 3600)

    dose_conc = calc_dose_conc(dose, molecular_mass, DV)
    time_conc = [list(a) for a in zip(time, dose_conc)]


    model = OneCompModel(time_conc, ke, cur_comp.k_abs)
    amount_unabs = model.calc_unabs(t)
    delta_abs = model.delta_abs(amount_unabs)

    X, infodict = model.integrate(t)

    return HttpResponse(X)


class CompoundView(viewsets.ModelViewSet):  # add this
    serializer_class = CompoundSerializer  # add this
    queryset = Compound.objects.all()

