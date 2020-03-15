from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('update', views.update_model, name='update_model'),
    path('calc_conc', views.calc_conc, name='calc_conc')
]
