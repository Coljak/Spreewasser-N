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