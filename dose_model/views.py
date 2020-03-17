import subprocess
import numpy as np
from django.http import HttpResponse
from dose_model.dose_model.helpers import calc_dose_conc, trans_thalf_ke
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CompoundTypeSerializer, CompoundSerializer, ConcentrationModelSerializer
from .models import CompoundType, Compound, ConcentrationModel
import json


from dose_model.dose_model.models import OneCompModel

# Create your views here.
update_model_sh = '../dose_model/static/dose_model/update_model.sh'


def home(request):
    return HttpResponse("Welcome")


def update_model(request):
    subprocess.Popen([update_model_sh], shell=True)
    return HttpResponse("models.py updated!")


def calc_conc(request):
    # GET parameters from request
    # compound
    compound = request.GET.get("compound")
    print(compound)
    # dose
    dose = json.loads((request.GET.get("dosage")))  # grams, seconds
    dose = list(map(float, dose))
    print("DOSE", dose)
    # time
    time = json.loads(request.GET.get("time"))
    time = list(map(int, time))
    # patient mass
    mass = float(request.GET.get("weight"))

    # feed params into ConcentrationModel object and calculate concentration
    cur_model = ConcentrationModel()
    cur_model = ConcentrationModel.create_cur_model(cur_model, doses=dose, time=time, mass=mass, compound=compound)
    print("calc_conc")
    cur_model = cur_model.calc_conc_model()
    X = json.loads(cur_model.conc)
    print(X)
    cur_model.save()

    return HttpResponse(X)


class CompoundTypeView(viewsets.ModelViewSet):
    serializer_class = CompoundTypeSerializer
    queryset = CompoundType.objects.all()

class CompoundView(viewsets.ModelViewSet):
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()

class ConcentrationModelView(viewsets.ModelViewSet):
    serializer_class = ConcentrationModelSerializer
    queryset = ConcentrationModel.objects.all()

