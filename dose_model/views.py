import subprocess
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from .serializers import CompoundTypeSerializer, CompoundSerializer, ConcentrationModelSerializer
from .models import CompoundType, Compound, ConcentrationModel
import dateutil.parser
import json




def home(request):
    return HttpResponse("Welcome")


def update_model(request):
    update_model_sh = './update_model.sh'
    subprocess.Popen([update_model_sh], shell=True)
    return HttpResponse("kinetics_models.py updated!")


def calc_conc(request):
    # GET parameters from request
    # compound
    compound = request.GET.get("compound")
    # dose
    dose = float(request.GET.get("dosage"))  # grams, seconds
    # time
    time = request.GET.get("time")
    time = dateutil.parser.parse(time)
    # patient mass
    mass = float(request.GET.get("weight"))

    # feed params into ConcentrationModel object and calculate concentration
    cur_model = ConcentrationModel()
    cur_model = ConcentrationModel.create_cur_model(cur_model, doses=dose, time=time, mass=mass, compound=compound)
    cur_model = cur_model.calc_conc_model()
    X = json.loads(cur_model.conc)

    serializer = ConcentrationModelSerializer(cur_model)

    return JsonResponse(serializer.data, safe=False)


class CompoundTypeView(viewsets.ModelViewSet):
    serializer_class = CompoundTypeSerializer
    queryset = CompoundType.objects.all()


class CompoundView(viewsets.ModelViewSet):
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()


class ConcentrationModelView(viewsets.ModelViewSet):
    serializer_class = ConcentrationModelSerializer
    queryset = ConcentrationModel.objects.all()

