from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
from djgeojson.views import GeoJSONLayerView
from . import views
from . import models

# template tagging
app_name = 'toolbox'


urlpatterns = [
    path('toolbox/', views.toolbox_dashboard, name='toolbox_dashboard'),
    path('toolbox/save-user-field/', views.save_user_field, name='save-user-field'),
    path('toolbox/get-user-fields/', views.get_user_fields, name='get-user-fields'),
    path('toolbox/update-user-field/<int:id>/', views.update_user_field, name='update-user-field'),
    path('toolbox/delete-user-field/<int:id>/', views.delete_user_field, name='delete-user-field'),
    path('toolbox/field-projects-menu/<int:id>/', views.get_field_project_modal, name='field_projects_menu'),
    path('toolbox/get_options/<str:parameter>/', views.get_options, name='get-options'),

    path('toolbox/save-project/', views.save_toolbox_project, name='save-project'),
    path('toolbox/load-project/<int:id>/', views.load_toolbox_project, name='load-project'),
    path('toolbox/load_polygon/', views.load_nuts_polygon, name='load_nuts_polygon'),
    path('toolbox/load_polygon/<str:entity>/<int:polygon_id>/', views.load_nuts_polygon, name='load_nuts_polygon_entity'),
    path('toolbox/filter_sinks/', views.filter_sinks, name='filter_sinks'),
    path('toolbox/filter_enlarged_sinks/', views.filter_enlarged_sinks, name='filter_enlarged_sinks'),
    path('toolbox/filter_streams/', views.filter_streams, name='filter_streams'),
    path('toolbox/filter_lakes/', views.filter_lakes, name='filter_lakes'),
    # path('toolbox/get_sinks_within/<int:user_field_id>/', views.toolbox_get_sinks_within, name='toolbox_get_sinks_within'),
    path('toolbox/load_infiltration_gui/<str:user_field_id>/', views.load_infiltration_gui, name='load_infiltration_gui'),
    path('toolbox/get_weighting_form/', views.get_weighting_forms, name='get_weighting_forms'),
    # path('toolbox/calculate_index_for_selection/', views.calculate_index_for_selection, name='calculate_index_for_selection'),
    path('toolbox/get_inlets/', views.get_inlets, name='get_inlets'),
]
