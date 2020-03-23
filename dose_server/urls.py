"""dose_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from dose_model import views as dose_model_views

router = routers.DefaultRouter()
router.register(r'compound', dose_model_views.CompoundView, 'compound')
router.register(r'compoundtype', dose_model_views.CompoundTypeView, 'compoundtype')
router.register(r'concentrationmodel', dose_model_views.ConcentrationModelView, 'concentrationmodel')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dose_model.urls')),
    path('plot/', include('plot_dose.urls')),
    path('api/', include(router.urls))
]
