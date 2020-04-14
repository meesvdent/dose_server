from django.conf.urls import url
from . import views


urlpatterns = [
    #url('', views.get_dose, name="get_dose"),
    url(r"^dose/$", views.dose_chart, name="dose_chart"),
    url(r"^dose_form/$", views.get_dose, name="get_dose"),
    url(r"^chartjs-scroll/$", views.test_chartjs_scroll, name='chartjs-scroll')
]

