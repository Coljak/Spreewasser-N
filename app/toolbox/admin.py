from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin, ModelAdmin
from . import models





class Lake4326Admin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'shape_area', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days' )
    list_filter = ['shape_area', 'shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
    ordering = ['min_surplus_volume']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6

class Stream4326Admin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days' )
    list_filter = ['shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
    ordering = ['min_surplus_volume']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6


admin.site.register(models.Lake4326, Lake4326Admin)
admin.site.register(models.Stream4326, Stream4326Admin)
