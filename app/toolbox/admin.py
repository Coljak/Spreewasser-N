from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin, ModelAdmin
from . import models




@admin.register(models.Lake)
class LakeAdmin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'shape_area', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days' )
    list_filter = ['shape_area', 'shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
    ordering = ['min_surplus_volume']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6

@admin.register(models.Stream)
class StreamAdmin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days' )
    list_filter = ['shape_length', 'min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
    ordering = ['min_surplus_volume']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6


@admin.register(models.Sink)
class SinkAdmin(LeafletGeoAdmin):
    list_display = ('id', 'shape_length', 'area', 'volume', 'index_1', 'index_2', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage')
    list_filter = ['area', 'shape_length', 'volume', 'index_1', 'index_2', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage']
    ordering = ['area']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6

@admin.register(models.EnlargedSink)
class EnlargedSinkAdmin(LeafletGeoAdmin):
    list_display = ('id', 'nat_length', 'area', 'volume', 'index_1', 'index_2', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage', 'land_use_4', 'land_use_4_percentage')
    list_filter = [ 'nat_length', 'area', 'volume', 'index_1', 'index_2', 'land_use_1', 'land_use_1_percentage','land_use_2', 'land_use_2_percentage', 'land_use_3', 'land_use_3_percentage', 'land_use_4', 'land_use_4_percentage']
    ordering = ['area']
    list_per_page = 100
    map_width = 800
    map_height = 600
    default_lat = 50.0
    default_lon = 10.0
    default_zoom = 6


@admin.register(models.SoilProperties)
class SoilPropertiesAdmin(LeafletGeoAdmin):
    list_display = ('id', 'nitrate_contamination', 'waterlog', 'groundwater_distance', 'hydraulic_conductivity_1m_rating', 'hydraulic_conductivity_2m_rating', 'fieldcapacity', 'agricultural_landuse', 'landuse')
    list_filter = ['id', 'nitrate_contamination', 'waterlog', 'groundwater_distance', 'hydraulic_conductivity_1m_rating', 'hydraulic_conductivity_2m_rating', 'fieldcapacity', 'agricultural_landuse', 'landuse']
    ordering = ['id']

@admin.register(models.SinkSoilProperties)
class SinkSoilPropertiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'sink', 'soil_properties', 'percent_of_total_area')
    # list_filter = ['percent_of_total_area']
    ordering = ['sink']
    search_fields = ['sink__id', 'soil_properties__id', 'percent_of_total_area']

@admin.register(models.EnlargedSinkSoilProperties)
class EnlargedSinkSoilPropertiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'enlarged_sink', 'soil_properties', 'percent_of_total_area')
    # list_filter = ['percent_of_total_area']
    ordering = ['enlarged_sink']
    search_fields = ['enlarged_sink__id', 'soil_properties__id', 'percent_of_total_area']

@admin.register(models.UserField)
class UserFieldAdmin(LeafletGeoAdmin):
    list_display = ('id', 'user', 'name', 'creation_date', 'geom', 'geom25833', 'has_infiltration', 'has_injection', 'has_sieker_sink', 'has_sieker_gek', 'has_sieker_surface_water', 'has_sieker_wetland', 'has_sieker_drainage')
    ordering = ['user', 'name']
    search_fields = ['user__username', 'name', 'creation_date', 'has_infiltration', 'has_injection', 'has_sieker_sink', 'has_sieker_gek', 'has_sieker_surface_water', 'has_sieker_wetland', 'has_sieker_drainage']

@admin.register(models.ToolboxProject)
class ToolboxProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'description', 'creation_date', 'user_field', 'toolbox_type',  'last_modified', 'project_data')
    list_filter = ['creation_date', 'last_modified']
    ordering = ['user', 'name', 'creation_date',  'toolbox_type', 'last_modified']
    search_fields = ['user__username', 'name', 'creation_date', 'last_modified', 'user_field', 'toolbox_type']


@admin.register(models.TimeseriesDailyQ)
class TimeseriesDailyQAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'date', 'amount')
    list_filter = ['station', 'date']
    ordering = ['station', 'date']
    search_fields = ['station__name', 'date', 'amount']

@admin.register(models.TimeseriesDailyWaterlevel)
class TimeseriesDailyWaterlevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'date', 'level')
    list_filter = ['station', 'date']
    ordering = ['station', 'date']
    search_fields = ['station__name', 'date', 'level']

@admin.register(models.TimeseriesMonthlyWaterlevel)
class TimeseriesMonthlyWaterlevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'month', 'level')
    list_filter = ['station', 'month']
    ordering = ['station', 'month']
    search_fields = ['station__name', 'month', 'level']

@admin.register(models.TimeseriesYearlyWaterlevel)
class TimeseriesYearlyWaterlevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'year', 'level')
    list_filter = ['station', 'year']
    ordering = ['station', 'year']
    search_fields = ['station__name', 'year', 'level']

@admin.register(models.TimeseriesValues)
class TimeseriesValuesAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'date', 'rainfall', 'waterlevel_above_sensor_cm', 'absolute_water_level_elevation_m')
    list_filter = ['station', 'date']
    ordering = ['station', 'date']
    search_fields = ['station__name', 'date', 'rainfall', 'waterlevel_above_sensor_cm', 'absolute_water_level_elevation_m']

@admin.register(models.LowerSpreeCachment)
class LowerSpreeCachmentAdmin(LeafletGeoAdmin):
    list_display = ('id', 'area', 'perimeter', 'geom4326')
    list_filter = ['area', 'perimeter',]
    ordering = ['id', 'area', 'perimeter',]
    search_fields = ['id', 'area', 'perimeter',]

@admin.register(models.Aquifer)
class AquiferAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_de', 'name_en')
    list_filter = ['name', 'name_de', 'name_en']
    ordering = ['name']
    search_fields = ['name', 'name_de', 'name_en']

@admin.register(models.DataInfoProperty)
class DataInfoPropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_data_info_type', 'order_position', 'popup', 'table', 'title_de', 'title_en', 'unit', 'value_name', 'href')
    list_filter = ['data_info', 'table', 'value_name']
    ordering = ['id', 'order_position', 'data_info']
    search_fields = ['data_info__data_type', 'order_position', 'popup', 'table', 'title_de', 'title_en', 'unit', 'value_name', 'href']

    @admin.display(description="Data Info Type")  # nicer header in admin
    def get_data_info_type(self, obj):
        return obj.data_info.data_type if obj.data_info else "-"

@admin.register(models.EnlargedSinkEmbankment)
class EnlargedSinkEmbankmentAdmin(LeafletGeoAdmin):
    list_display = ('id', 'fid_sink', 'height', 'plat_width', 'volume', 'enlarged_sink')
    search_fields = ('fid_sink',)
    list_filter = ('enlarged_sink',)
    ordering = ('fid_sink',)


@admin.register(models.Feasibility)
class FeasibilityAdmin(LeafletGeoAdmin):
    list_display = ('id', 'landuse', 'vegetation', 'soil_quality_index', 'index_feasibility')
    list_filter = ('vegetation', 'landuse')
    search_fields = ('landuse__name',)


@admin.register(models.GekRetention)
class GekRetentionAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'association', 'planning_segment', 'gek_document', 'number_of_measures')
    list_filter = ('association', 'planning_segment')
    search_fields = ('name', 'association', 'planning_segment')
    ordering = ('id',)


@admin.register(models.GekRetentionMeasure)
class GekRetentionMeasureAdmin(admin.ModelAdmin):
    list_display = ('id', 'gek_retention', 'gek_measure', 'quantity', 'priority', 'costs')
    list_filter = ('priority',)
    search_fields = ('description_de',)
    ordering = ('id',)


@admin.register(models.HistoricalWetlands)
class HistoricalWetlandsAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'association', 'area', 'feucht_per', 'feasibility')
    search_fields = ('name', 'association')
    list_filter = ('association',)
    ordering = ('id',)


@admin.register(models.Hydrogeology)
class HydrogeologyAdmin(LeafletGeoAdmin):
    list_display = ('id', 'aq_complex', 'aquifer', 'index')
    search_fields = ('aq_complex', 'aquifer')
    ordering = ('id',)


@admin.register(models.Lake25)
class Lake25Admin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'wa_cd', 'genese', 'area_gis', 'wrrl_pg')
    search_fields = ('name', 'wa_cd', 'genese')
    list_filter = ('wa_cd', 'genese')
    ordering = ('id',)


@admin.register(models.LanduseCLC2018)
class LanduseCLC2018Admin(LeafletGeoAdmin):
    list_display = ('id', 'clc18', 'name_de', 'shape_area')
    search_fields = ('clc18', 'name_de')
    ordering = ('id',)


@admin.register(models.LanduseMap)
class LanduseMapAdmin(LeafletGeoAdmin):
    list_display = ('id', 'landuse', 'vegetation')
    list_filter = ('vegetation',)
    search_fields = ('landuse__name',)
    ordering = ('id',)


@admin.register(models.SiekerLargeLake)
class SiekerLargeLakeAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'area_m2', 'area_ha', 'd_max_m', 'vol_mio_m3')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(models.SiekerSink)
class SiekerSinkAdmin(LeafletGeoAdmin):
    list_display = ('id', 'fid', 'volume', 'area', 'depth', 'urbanarea_percent', 'wetlands_percent')
    list_filter = ('urbanarea', 'wetlands')
    search_fields = ('fid',)
    ordering = ('id',)


@admin.register(models.SiekerWaterLevel)
class SiekerWaterLevelAdmin(LeafletGeoAdmin):
    list_display = ('id', 'messstelle', 'gewaesser', 'start_date', 'end_date', 'twenty_yr_trend')
    search_fields = ('messstelle', 'gewaesser')
    list_filter = ('region',)
    ordering = ('id',)

@admin.register(models.BelowGroundWaters)
class BelowGroundWatersAdmin(LeafletGeoAdmin):
    list_display = ('id', 'kennzahl', 'gewaesser', 'gew_alias', 'geom')
    search_fields = ('gewaesser',)
    ordering = ('id',)


# ---------------------------
# NON-SPATIAL MODELS
# ---------------------------

@admin.register(models.GekDocument)
class GekDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'publisher', 'year_of_publication')
    search_fields = ('link', 'publisher')
    ordering = ('year_of_publication',)


@admin.register(models.Hydromorphy)
class HydromorphyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating_index')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(models.LeafletLegend)
class LeafletLegendAdmin(admin.ModelAdmin):
    list_display = ('id', 'header_de', 'header_en')
    search_fields = ('header_de', 'header_en')


@admin.register(models.LegendGrade)
class LegendGradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'leaflet_legend', 'value', 'label_de', 'order_position')
    list_filter = ('leaflet_legend',)
    ordering = ('leaflet_legend', 'order_position')


@admin.register(models.MapLabels)
class MapLabelsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'map_name', 'map_value', 'order_position')
    list_filter = ('map_name',)
    search_fields = ('name', 'label_de', 'label_en')
    ordering = ('map_name', 'order_position')


@admin.register(models.MarSliderDescription)
class MarSliderDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_de', 'name_en', 'weight')
    search_fields = ('name_de', 'name_en')
    ordering = ('id',)


@admin.register(models.MarSuitabilitySliderDescription)
class MarSuitabilitySliderDescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_de', 'name_en', 'suitability')
    search_fields = ('name_de', 'name_en')
    ordering = ('id',)


@admin.register(models.SoilTexture)
class SoilTextureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating_index')
    search_fields = ('name',)
    ordering = ('name',)

# ---------------------------
# HYDROLOGY / STATIONS
# ---------------------------

@admin.register(models.Station)
class StationAdmin(LeafletGeoAdmin):
    list_display = (
        'id', 'name', 'waterbody', 'data_provider',
        'absolute_elevation_of_sensor_m', 'gauge_zero', 'station_number'
    )
    search_fields = ('name', 'waterbody', 'data_provider')
    list_filter = ('data_provider',)
    ordering = ('name',)


# ---------------------------
# ORGANIZATIONAL / ENTITIES
# ---------------------------

@admin.register(models.WaterCoordinationEntity)
class WaterCoordinationEntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'short', 'name')
    search_fields = ('short', 'name')
    ordering = ('short',)


# ---------------------------
# GEK / LANDUSE RELATIONS
# ---------------------------

@admin.register(models.GekLanduse)
class GekLanduseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'gek_retention', 'current_landuse', 'clc_landuse',
        'first_two_clc_digits', 'area_total', 'area_of_landuse', 'area_percentage'
    )
    list_filter = ('first_two_clc_digits', 'clc_landuse')
    search_fields = (
        'current_landuse', 'gek_retention__name',
        'clc_landuse__name_de', 'clc_landuse__name_en'
    )
    ordering = ('gek_retention',)


# ---------------------------
# GEK PRIORITY / MEASURES
# ---------------------------

@admin.register(models.GekPriority)
class GekPriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'description_de', 'description_en', 'priority_level')
    list_filter = ('priority_level',)
    search_fields = ('description_de', 'description_en')
    ordering = ('priority_level',)


@admin.register(models.GEKMeasures)
class GEKMeasuresAdmin(admin.ModelAdmin):
    list_display = ('id', 'description_de',)
    search_fields = ('description_de',)
    ordering = ('id',)


# ---------------------------
# FEASIBILITY / ECOLOGY
# ---------------------------

# @admin.register(models.WetlandFeasibility)
# class WetlandFeasibilityAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name_de', 'name_en', 'index')
#     search_fields = ('name_de', 'name_en')
#     ordering = ('index',)


@admin.register(models.WetGrassland)
class WetGrasslandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating_index')
    search_fields = ('name',)
    ordering = ('name',)


admin.site.register(models.OutlineInjection, LeafletGeoAdmin)
admin.site.register(models.OutlineSurfaceWater, LeafletGeoAdmin)
admin.site.register(models.OutlineInfiltration, LeafletGeoAdmin)
admin.site.register(models.Landuse, admin.ModelAdmin)

admin.site.register(models.MarForbiddenArea, LeafletGeoAdmin)



admin.site.register(models.LanduseSink, LeafletGeoAdmin)
admin.site.register(models.LanduseEnlargedSink, LeafletGeoAdmin)
admin.site.register(models.HydrogeologySinks, LeafletGeoAdmin)
admin.site.register(models.HydrogeologyEnlargedSinks, LeafletGeoAdmin)
admin.site.register(models.GroundWaterDistanceClass, admin.ModelAdmin)

admin.site.register(models.AgriculturalLanduse, admin.ModelAdmin)
