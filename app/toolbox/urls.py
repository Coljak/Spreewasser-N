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
    path('startpage/', views.toolbox_start, name='toolbox_start'),
    path('dashboard/', views.toolbox_dashboard, name='toolbox_dashboard'),
    path('login/Dashboard/toolbox_sinks/', views.load_toolbox_sinks, name='load_toolbox_sinks'),
    path('login/Dashboard/toolbox_outline_injection/', views.load_outline_injection, name='load_outline_injection'),
    path('login/Dashboard/load_outline_surface_water/', views.load_outline_surface_water, name='load_outline_surface_water'),
    path('login/Dashboard/load_outline_infiltration/', views.load_outline_infiltration, name='load_outline_infiltration'),
    path('login/Dashboard/load_outline_geste/', views.load_outline_geste, name='load_outline_geste'),
    path('login/Dashboard/load_outline_water_retention/', views.load_outline_water_retention, name='load_outline_water_retention'),
    path('login/Dashboard/toolbox-edit/<int:id>/', views.toolbox_sinks_edit, name='toolbox_project_edit'),
    path('login/Dashboard/toolbox_get_sinks_within/<int:area_id>/', views.toolbox_get_sinks_within, name='toolbox_get_sinks_within'),
    path('login/Dashboard/sinks_filter/', views.sinks_filter, name='sinks_filter'),

    ]
