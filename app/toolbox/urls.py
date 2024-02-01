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
    path('startpage/', views.toolbox_dashboard, name='toolbox_dashboard'),
    ]
