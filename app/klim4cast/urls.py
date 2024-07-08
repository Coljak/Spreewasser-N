from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.contrib.auth.views import LoginView, LogoutView
from djgeojson.views import GeoJSONLayerView
from . import views
from . import models

# template tagging
app_name = 'klim4cast'

urlpatterns = [
    # general paths
    path('', views.klim4cast, name='klim4cast'),
    path('Timelapse/', views.klim4cast_timelapse_items, name='timelapse-page'),
    path('get_ncml_metadata/<str:name>', views.get_ncml_metadata, name='get-ncml-metadata'),
    path('Timelapse/Thredds/wms/<str:netcdf>', views.timelapse_django_passthrough_wms, name='timelapse-passthrough-wms'),
    
]