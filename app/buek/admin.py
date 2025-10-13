from django.contrib import admin
from . import models
from leaflet.admin import LeafletGeoAdmin

class BulkDensityClassAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'bulk_density_class', 'raw_density_g_per_cm3')
class Ka5TextureClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'ka5_soiltype', 'sand', 'silt', 'clay')

class CapillaryRiseAdmin(admin.ModelAdmin):
    list_display = ('id', 'soil_type', 'ka5textureclass', 'distance', 'capillary_rate')
    list_filter = ('soil_type', 'ka5textureclass', 'distance', 'capillary_rate')

    def get_ka5textureclass_name(self, obj):
        return obj.ka5textureclass.name if obj.ka5textureclass else "No ka5textureclass Assigned"
    get_ka5textureclass_name.short_description = 'Ka5TextureClass Name' 

class HumusClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'humus_class', 'corg')
    
class PHClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'ph_class', 'ph_lower_value', 'ph_upper_value')

class BuekPolygonAdmin(admin.ModelAdmin):
    list_display = ('polygon_id', 'bgl', 'symbol', 'legende')

class CorineLandCover2018Admin(admin.ModelAdmin):
    list_display = ('id', 'label_level_1', 'label_level_2', 'label_level_3', 'label_de', 'corine_landcover_code')

class SoilProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'system_unit', 'legacy_bodsysteinh', 'legacy_bodtyp', 'legacy_bo_subtyp', 'legacy_bo_subtyp_txt', 'area_percentage', 'landusage_corine_code')
    list_filter = ('system_unit', 'legacy_bodsysteinh', 'legacy_bodtyp', 'legacy_bo_subtyp', 'legacy_bo_subtyp_txt', 'area_percentage', 'landusage_corine_code')

class SoilProfileHorizonAdmin(admin.ModelAdmin):
    list_display = ('id', 'soilprofile', 'horizont_nr', 'obergrenze_m', 'untergrenze_m', 'symbol', 'bulk_density_class', 'ka5_texture_class', 'humus_class', 'ph_class')
    list_filter = ('soilprofile', 'bulk_density_class', 'ka5_texture_class', 'humus_class', 'ph_class')

    def get_bulk_density_class_name(self, obj):
        return obj.bulk_density_class.bulk_density_class if obj.bulk_density_class else "No bulk_density_class Assigned"
    get_bulk_density_class_name.short_description = 'BulkDensityClass'

    def get_ka5_texture_class_name(self, obj):
        return obj.ka5_texture_class.ka5_soiltype if obj.ka5_texture_class else "No ka5_texture_class Assigned"
    get_ka5_texture_class_name.short_description = 'Ka5TextureClass'

    def get_humus_class_name(self, obj):
        return obj.humus_class.humus_class if obj.humus_class else "No humus_class Assigned"
    
class MapSoilCLCAdmin(LeafletGeoAdmin):
    list_display = ('id', 'tkle_nr', 'polygon', 'corine_landcover_code', 'clc_code', 'bias_21_clc_code', 'bias_23_clc_code', 'bias_31_clc_code')
    list_filter = ('tkle_nr', 'polygon', 'corine_landcover_code', 'clc_code', 'bias_21_clc_code', 'bias_23_clc_code', 'bias_31_clc_code')

    def get_corine_landcover_code_name(self, obj):
        return obj.corine_landcover_code.__str__() if obj.corine_landcover_code else "No CLC Assigned"
class CLCMap2018Admin(admin.ModelAdmin):
    list_display = ('id', 'geom', 'code_18', 'fid', 'objectid')
    list_filter = ('code_18', 'fid', 'objectid')


    

admin.site.register(models.BulkDensityClass, BulkDensityClassAdmin)
admin.site.register(models.Ka5TextureClass, Ka5TextureClassAdmin)
admin.site.register(models.CapillaryRise, CapillaryRiseAdmin)
admin.site.register(models.HumusClass, HumusClassAdmin)
admin.site.register(models.PHClass, PHClassAdmin)
admin.site.register(models.BuekPolygon, BuekPolygonAdmin)
admin.site.register(models.Buek200, LeafletGeoAdmin)
admin.site.register(models.CorineLandCover2018, CorineLandCover2018Admin)
admin.site.register(models.SoilProfile, SoilProfileAdmin)
admin.site.register(models.SoilProfileHorizon, SoilProfileHorizonAdmin)
admin.site.register(models.MapSoilCLC, MapSoilCLCAdmin)
admin.site.register(models.CLCMap2018, CLCMap2018Admin)

