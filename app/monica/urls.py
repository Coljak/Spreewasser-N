from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views
from . import models

# template tagging
app_name = 'monica'

urlpatterns = [
    path('monica_calc_w_params_from_db/', views.monica_calc_w_params_from_db, name='monica_calc_w_params_from_db'),
    path('get_cultivar_parameters/<int:id>/', views.get_cultivar_parameters, name='get_cultivar_parameters'),
    path('model/', views.monica_model, name='monica_model'),
    path('model/<str:model_name>/<int:id>/', views.modify_model_parameters, name='modify_model_parameters'),
    # path('cultivar_parameters/<int:id>/', views.cultivar_parameters, name='cultivar_parameters'),
    path('crop_residue_parameters/<int:id>/', views.crop_residue_parameters, name='crop_residue_parameters'),
    path('add_workstep/', views.add_workstep, name='add_workstep'),
    # path('add_workstep/<str:workstep_type>/', views.add_workstep, name='add_workstep'),
    path('model/get_options/<str:parameter_type>/', views.get_parameter_options, name='get_parameter_options'),
]