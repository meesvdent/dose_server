import django
from django.conf.urls import url
from django.views.generic import TemplateView

from pkg_resources import parse_version

from . import views

urlpatterns = [
    url(r"^dose/$", views.dose_chart, name="dose_chart"),
    #url(r"^dose/json/$", views.dose_chart_json, name="dose_chart_json"),
    url(r"^dose_form/$", views.get_dose, name="get_dose")
]

