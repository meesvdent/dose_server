from django.shortcuts import render
import subprocess
from django.templatetags.static import static
from django.http import HttpResponse


# Create your views here.
update_model_sh = '/Users/meesvdent/Developer/dose_server/dose_model/static/dose_model/update_model.sh'


def home(request):
    return HttpResponse("Welcome")


def update_model(request):
    subprocess.Popen([update_model_sh], shell=True)
    return HttpResponse("models.py updated!")




