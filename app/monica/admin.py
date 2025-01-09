from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin, ModelAdmin
from . import models


admin.site.register(models.CropParametersExist, admin.ModelAdmin)
admin.site.register(models.SpeciesParameters, admin.ModelAdmin)
admin.site.register(models.CultivarParameters, admin.ModelAdmin)
admin.site.register(models.CropResidueParameters, admin.ModelAdmin)
admin.site.register(models.OrganFromDB, admin.ModelAdmin)
admin.site.register(models.OrganicFertiliser, admin.ModelAdmin)
admin.site.register(models.MineralFertiliser, admin.ModelAdmin)
admin.site.register(models.UserCropParameters, admin.ModelAdmin)
admin.site.register(models.UserEnvironmentParameters, admin.ModelAdmin)
admin.site.register(models.UserSoilMoistureParameters, admin.ModelAdmin)
admin.site.register(models.UserSoilOrganicParameters, admin.ModelAdmin)
admin.site.register(models.SoilTemperatureModuleParameters, admin.ModelAdmin)
admin.site.register(models.SimulationEnvironment, admin.ModelAdmin)
admin.site.register(models.DWDGridToPointIndices, LeafletGeoAdmin)
# admin.site.register(models.DigitalElevationModel, admin.ModelAdmin)
admin.site.register(models.UserSoilProfile, admin.ModelAdmin)
# admin.site.register(models.SoilProfileLayer, admin.ModelAdmin)
admin.site.register(models.MonicaSite, admin.ModelAdmin)


"""
([{'Thickness': [0.15, 'm'], 'Sand': [0.34, '%'], 'Clay': [0.21, '%'], 'pH': 6.45, 'KA5TextureClass': 'Ls2', 'SoilRawDensity': [1500.0, 'kg m-3'], 'SoilOrganicCarbon': [5.75, '%']}, {'Thickness': [0.15, 'm'], 'Sand': [0.34, '%'], 'Clay': [0.21, '%'], 'pH': 6.45, 'KA5TextureClass': 'Ls2', 'SoilRawDensity': [1500.0, 'kg m-3'], 'SoilOrganicCarbon': [3.49, '%']}, {'Thickness': [0.4, 'm'], 'Sand': [0.3, '%'], 'Clay': [0.3, '%'], 'pH': 7.55, 'KA5TextureClass': 'Lt2', 'SoilRawDensity': [1900.0, 'kg m-3'], 'SoilOrganicCarbon': [0.29, '%']}, {'Thickness': [1.3, 'm'], 'Sand': [0.93, '%'], 'Clay': [0.02, '%'], 'pH': 7.55, 'KA5TextureClass': 'Ss', 'SoilRawDensity': [1700.0, 'kg m-3'], 'SoilOrganicCarbon': [0.0, '%']}], None)
"""