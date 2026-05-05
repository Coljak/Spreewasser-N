from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views
from . import models
from buek import views as buek_views

# template tagging
app_name = 'monica'

urlpatterns = [
    path('', views.monica_model, name='monica_model'),
    # path('modify-parameter/', views.modify_model_parameters, name='modify_model_parameters'),
    path('load-project/<int:id>/', views.load_monica_project, name='load_monica_project'),
    path('save-project/', views.save_project, name='save-monica-project'),
    path('delete-project/<int:id>/', views.delete_monica_project, name='delete_monica_project'),
    path('get-soil-profile-form/', views.get_soil_profile_form, name='get_soil_profile_form'),
    path('get-recommended-soil-profile/', views.get_recommended_soil_profile, name='get_soil_profile'),
    path('get-recommended-soil-profile-id/<str:lat>/<str:lon>/', buek_views.get_recommended_soil_profile_id, name='get_recommended_soil_profile_id'),
    path('get-soil-profile-landusage-choices/', views.get_soil_profile_landusage_choices, name='get_soil_profile_landusage_choices'),
    path('get-soil-profile-area-percentage-choices/', views.get_soil_profile_area_percentage_choices, name='get_soil_profile_area_percentage_choices'),
    path('get-soil-profile-system-unit-choices/', views.get_soil_profile_system_unit_choices, name='get_soil_profile_system_unit_choices'),
    path('get-soil-profile-choices/', views.get_soil_profile_choices, name='get_soil_profile_choices'),
    path('get-soil-profile-info/<int:profile_id>/', views.get_soil_profile_info, name='get_soil_profile_info'),
    path('save-soil-profile/', views.save_soil_profile, name='save_soil_profile'),

    path('select-soil-profile/<str:lat>/<str:lon>/', views.manual_soil_selection, name='manual-soil-selection'),
    path('get-slope/<str:lat>/<str:lon>/', views.get_slope, name='get_slope'),
    path('get-altitude/<str:lat>/<str:lon>/', views.get_altitude, name='get_altitude'),
    path('get-n-deposition/<str:lat>/<str:lon>/', views.get_n_deposition, name='get_n_deposition'),
    path('<str:parameter>/<int:id>/<int:rotation>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('<str:parameter>/<int:id>/', views.modify_model_parameters, name='modify_model_parameters'),
    # path('model/<str:parameter>/', views.modify_model_parameters, name='modify_model_parameters'),
    path('get_options/<str:parameter_type>/', views.get_parameter_options, name='get_parameter_options'),
    path('get_options/<str:parameter_type>/<int:id>/', views.get_parameter_options, name='get_parameter_options'),
    # path('model/save_simulation_settings/', views.save_simulation_settings, name='save_simulation_settings'),
    
    path('run-simulation/', views.run_simulation, name='run_simulation'),
    path('download_irrigation_csv/', views.download_irrigation_csv, name='download_irrigation_csv'),
    
    path(('monica_run_over_germany/'), views.monica_run_over_germany, name='monica_run_over_germany'),
]


