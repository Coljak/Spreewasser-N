from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
from djgeojson.views import GeoJSONLayerView
from . import views
from . import models

# template tagging
app_name = 'toolbox'

# urlpatterns = [
#     path('dashboard/', views.toolbox_dashboard, name='toolbox_dashboard'),
#     path('login/Dashboard/toolbox_sinks/', views.load_toolbox_sinks, name='load_toolbox_sinks'),
#     path('login/Dashboard/toolbox_outline_injection/', views.load_outline_injection, name='load_outline_injection'),
#     path('login/Dashboard/load_outline_surface_water/', views.load_outline_surface_water, name='load_outline_surface_water'),
#     path('login/Dashboard/load_outline_infiltration/', views.load_outline_infiltration, name='load_outline_infiltration'),
#     path('login/Dashboard/load_outline_geste/', views.load_outline_geste, name='load_outline_geste'),
#     path('login/Dashboard/load_outline_water_retention/', views.load_outline_water_retention, name='load_outline_water_retention'),
#     path('login/Dashboard/toolbox-edit/<int:id>/', views.toolbox_sinks_edit, name='toolbox_project_edit'),
#     path('login/Dashboard/toolbox_get_sinks_within/<int:area_id>/', views.toolbox_get_sinks_within, name='toolbox_get_sinks_within'),
#     path('login/Dashboard/sinks_filter/', views.sinks_filter, name='sinks_filter'),
#     path('toolbox/', views.three_split, name='three_split'),
#     path('toolbox/load/', views.get_user_fields, name='load_user_fields'),
#     path('toolbox/save/', views.save_user_field, name='save_user_field'),

#     ]

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
    # path('toolbox/get_selected_sinks/', views.get_selected_sinks, name='get_selected_sinks'),
    path('toolbox/test/', views.test, name='test'),
]
