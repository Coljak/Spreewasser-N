from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views
from . import models

# template tagging
app_name = 'monica'

urlpatterns = [
    path('', views.monica, name='monica'),
    path('hohenfinow/', views.monica_generate_hohenfinow, name='monica_hohenfinow'),
    path('hohenfinowdb/', views.monica_generate_hohenfinow_from_db, name='monica_hohenfinow_from_db'),
    path('monica_calc_w_params_from_db/', views.monica_calc_w_params_from_db, name='monica_calc_w_params_from_db'),
    path('hohenfinowFile/', views.monica_generate_from_env_file, name='monica_hohenfinow_from_file'),
    path('get_cultivar_parameters/<int:id>/', views.get_cultivar_parameters, name='get_cultivar_parameters'),
    # Bootstrap test colors
]