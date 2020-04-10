from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework import routers
from dose_model import views as dose_model_views
from users import views as user_views

router = routers.DefaultRouter()
router.register(r'compound', dose_model_views.CompoundView, 'compound')
router.register(r'compoundtype', dose_model_views.CompoundTypeView, 'compoundtype')
router.register(r'concentrationmodel', dose_model_views.ConcentrationModelView, 'concentrationmodel')
router.register(r'plasmaconcentrationmodel', dose_model_views.PlasmaConcentrationView, 'plasmaconcentrationmodel')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dose_model.urls')),
    path('plot/', include('plot_dose.urls')),
    path('api/', include(router.urls)),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout')
]
