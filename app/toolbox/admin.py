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

class Sink4326Admin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'area', 'volume', 'index_1', 'index_2', 'index_3', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage')
    list_filter = ['area', 'shape_length', 'volume', 'index_1', 'index_2', 'index_3', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage']
    ordering = ['area']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6

class EnlargedSink4326Admin(LeafletGeoAdmin):
    list_display = ('id', 'nat_length', 'area', 'volume', 'index_1', 'index_2', 'index_3', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage', 'land_use_4', 'land_use_4_percentage')
    list_filter = [ 'nat_length', 'area', 'volume', 'index_1', 'index_2', 'index_3', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage', 'land_use_4', 'land_use_4_percentage']
    ordering = ['area']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6


class SoilPropertiesAdmin(LeafletGeoAdmin):
    list_display = ('id', 'nitrate_contamination', 'waterlog', 'groundwater_distance', 'hydraulic_conductivity_1m_rating', 'hydraulic_conductivity_2m_rating', 'fieldcapacity', 'agricultural_landuse', 'landuse')
    list_filter = ['id', 'nitrate_contamination', 'waterlog', 'groundwater_distance', 'hydraulic_conductivity_1m_rating', 'hydraulic_conductivity_2m_rating', 'fieldcapacity', 'agricultural_landuse', 'landuse']
    ORDERING = ['id']

class SinkSoilPropertiesAdmin(ModelAdmin):
    list_display = ('id', 'sink', 'soil_properties', 'percent_of_total_area')
    # list_filter = ['percent_of_total_area']
    ordering = ['sink']
    search_fields = ['sink__id', 'soil_properties__id', 'percent_of_total_area']



admin.site.register(models.Sink4326, Sink4326Admin)
admin.site.register(models.EnlargedSink4326, EnlargedSink4326Admin)
admin.site.register(models.Lake4326, Lake4326Admin)
admin.site.register(models.Stream4326, Stream4326Admin)
admin.site.register(models.SoilProperties, SoilPropertiesAdmin)
admin.site.register(models.SinkSoilProperties, SinkSoilPropertiesAdmin)
