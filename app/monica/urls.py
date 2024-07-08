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
    path('form/', views.manage_rotation_steps, name='monica_form'),
    # path('add_workstep/<str:workstep_type>/', views.add_workstep, name='add_workstep'),
]