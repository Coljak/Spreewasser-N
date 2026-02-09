from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views
from . import models

# template tagging
app_name = 'monica'

urlpatterns = [
    path('', views.monica_model, name='monica_model'),
    # path('modify-parameter/', views.modify_model_parameters, name='modify_model_parameters'),
    path('load-project/<int:id>/', views.load_monica_project, name='load_monica_project'),
    path('save-project/', views.save_project, name='save-monica-project'),
    path('delete-project/<int:id>/', views.delete_monica_project, name='delete_monica_project'),
    path('recommended-soil-profile/<str:profile_landusage>/<str:lat>/<str:lon>/', views.get_soil_parameters, name='get_soil_parameters'),
    # path('soil-profile-recommended/', views.get_recommended_soil_profile, name='get_recommended_soil_profile'),
    path('get-soil-profile-form/', views.get_soil_profile_form, name='get_soil_profile_form'),
    path('get-soil-profile/', views.get_soil_profile, name='get_soil_profile'),
    path('save-soil-profile/', views.save_soil_profile, name='save_soil_profile'),
    # path('soil-profile/<str:lat>/<str:lon>/<int:id>/', views.get_soil_parameters, name='get_soil_parameters'),
    path('select-soil-profile/<str:lat>/<str:lon>/', views.manual_soil_selection, name='manual-soil-selection'),
    
    path('<str:parameter>/<int:id>/<int:rotation>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('<str:parameter>/<int:id>/', views.modify_model_parameters, name='modify_model_parameters'),
    # path('model/<str:parameter>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('get_options/<str:parameter_type>/', views.get_parameter_options, name='get_parameter_options'),
    path('get_options/<str:parameter_type>/<int:id>/', views.get_parameter_options, name='get_parameter_options'),
    # path('model/save_simulation_settings/', views.save_simulation_settings, name='save_simulation_settings'),
    
    path('run-simulation/', views.run_simulation, name='run_simulation'),
    path('download_irrigation_csv/', views.download_irrigation_csv, name='download_irrigation_csv'),
]


