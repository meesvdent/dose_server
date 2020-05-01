from django.urls import path, include
from . import views as compound_views

urlpatterns = [
    path(r"^compound/$", compound_views.compound, name='compound'),
    ]

