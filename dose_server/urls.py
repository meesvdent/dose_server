from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework import routers
from dose_model import views as dose_model_views
from users import views as user_views
from compounds import views as compound_views


router = routers.DefaultRouter()
router.register(r'compound', dose_model_views.CompoundView, 'compound')
router.register(r'compoundtype', dose_model_views.CompoundTypeView, 'compoundtype')
router.register(r'concentrationmodel', dose_model_views.ConcentrationModelView, 'concentrationmodel')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dose_model.urls')),
    path('plot/', include('plot_dose.urls')),
    path('api/plasmaconcentrationmodel/', dose_model_views.get_plasma_conc, name='get_plasma_conc'),
    path('api/', include(router.urls)),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('compounds/', compound_views.compound_view, name='compound_view'),
    path('compound/', compound_views.compound, name='compound')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)