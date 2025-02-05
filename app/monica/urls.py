from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views
from . import models

# template tagging
app_name = 'monica'

urlpatterns = [
    # path('monica_calc_w_params_from_db/', views.monica_calc_w_params_from_db, name='monica_calc_w_params_from_db'),
    # path('get_cultivar_parameters/<int:id>/', views.get_cultivar_parameters, name='get_cultivar_parameters'),
    path('', views.monica_model, name='monica_model'),
    # path('modify-parameter/', views.modify_model_parameters, name='modify_model_parameters'),
    path('load-project/<int:id>/', views.load_monica_project, name='load_monica_project'),
    path('save-project/', views.save_monica_project, name='save-monica-project'),
    path('delete-project/<int:id>/', views.delete_monica_project, name='delete_monica_project'),
    path('soil-profile/<str:lat>/<str:lon>/', views.get_soil_parameters, name='get_soil_parameters'),
    path('soil-profile/<str:lat>/<str:lon>/<int:id>/', views.get_soil_parameters, name='get_soil_parameters'),
    path('select-soil-profile/<str:lat>/<str:lon>/', views.manual_soil_selection, name='manual-soil-selection'),
    
    path('<str:parameter>/<int:id>/<int:rotation>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('<str:parameter>/<int:id>/', views.modify_model_parameters, name='modify_model_parameters'),
    # path('model/<str:parameter>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('get_options/<str:parameter_type>/', views.get_parameter_options, name='get_parameter_options'),
    path('get_options/<str:parameter_type>/<int:id>/', views.get_parameter_options, name='get_parameter_options'),
    # path('model/save_simulation_settings/', views.save_simulation_settings, name='save_simulation_settings'),
    
    path('run-simulation/', views.run_simulation, name='run_simulation'),
]
