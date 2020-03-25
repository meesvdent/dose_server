import subprocess
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from .serializers import CompoundTypeSerializer, CompoundSerializer, DoseModelSerializer, PlasmaConcentrationSerializer
from .models import CompoundType, Compound, Dose
import dateutil.parser




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

    # feed params into DoseModel object and calculate concentration
    cur_model = Dose()
    cur_model = Dose.create_cur_model(cur_model, doses=dose, time=time, mass=mass, compound=compound)
    cur_model = cur_model.calc_conc_model()

    # serialize cur_model
    dose_serializer = DoseModelSerializer(cur_model)

    # get conc from PlasmaConc database query referencing current dose
    plasma_conc_query = cur_model.plasma_conc.all()
    plasma_serializer = PlasmaConcentrationSerializer(plasma_conc_query, many=True)

    return JsonResponse([dose_serializer.data, plasma_serializer.data], safe=False)


class CompoundTypeView(viewsets.ModelViewSet):
    serializer_class = CompoundTypeSerializer
    queryset = CompoundType.objects.all()


class CompoundView(viewsets.ModelViewSet):
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()


class ConcentrationModelView(viewsets.ModelViewSet):
    serializer_class = DoseModelSerializer
    queryset = Dose.objects.all()

