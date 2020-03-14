from django.shortcuts import render
import subprocess


# Create your views here.

def update_model():
    subprocess.call("dose_model/update_model.sh")