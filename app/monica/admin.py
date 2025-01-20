from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin, ModelAdmin
from . import models


class BaseUserAdmin(admin.ModelAdmin):
    """Base admin class for shared logic and methods."""
    
    def get_user_name(self, obj):
        return obj.user.name if obj.user else "No User Assigned"
    get_user_name.short_description = 'User Name' 



class MonicaProjectAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'user', 'creation_date', 'last_modified', 'monica_model_setup',  'monica_site')
    list_filter = ('user', 'creation_date', 'last_modified')
    readonly_fields = ('creation_date', 'last_modified')


class CropParametersExistAdmin(admin.ModelAdmin):
    list_display = ('id', 'species_name', 'in_species', 'in_cultivar', 'in_residues')


class UserParametersAdmin(BaseUserAdmin):
    list_display = ('id','user', 'is_default')
    list_filter = ('user', 'is_default')

class UserParametersNameAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'user', 'is_default') 
    list_filter = ('user', 'is_default')

class UserSoilTransportParametersAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'user', 'is_default')
    list_filter = ('user', 'is_default')


class OrganFromDBAdmin(BaseUserAdmin):
    list_display = ('id', 'species_name', 'get_organ_name', 'user', 'is_default')
    list_filter = ('user', 'is_default')

    def get_organ_name(self, obj):
        return obj.organ.name if obj.organ else "No Organ Assigned"
    get_organ_name.short_description = 'Organ Name' 


class MonicaSiteAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'user', 'latitude', 'longitude')

class SiteParametersAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'user', 'latitude', 'longitude')
    list_filter = ('user')
 


admin.site.register(models.CropParametersExist, CropParametersExistAdmin)
admin.site.register(models.SpeciesParameters, UserParametersNameAdmin)
admin.site.register(models.CultivarParameters, UserParametersNameAdmin)
admin.site.register(models.CropResidueParameters, UserParametersNameAdmin)
admin.site.register(models.OrganFromDB, OrganFromDBAdmin)
admin.site.register(models.Organ, admin.ModelAdmin)
admin.site.register(models.OrganicFertiliser, UserParametersNameAdmin)
admin.site.register(models.MineralFertiliser, UserParametersNameAdmin)
admin.site.register(models.UserCropParameters, UserParametersNameAdmin)
admin.site.register(models.UserEnvironmentParameters, UserParametersNameAdmin)
admin.site.register(models.UserSimulationSettings, UserParametersNameAdmin)
admin.site.register(models.UserSoilMoistureParameters, UserParametersNameAdmin)
admin.site.register(models.UserSoilOrganicParameters, UserParametersNameAdmin)
admin.site.register(models.SoilTemperatureModuleParameters, UserParametersNameAdmin)
# admin.site.register(models.SimulationEnvironment, UserParametersAdmin)
admin.site.register(models.UserSoilTransportParameters, UserSoilTransportParametersAdmin)
# admin.site.register(models.SiteParameters, admin.ModelAdmin)


# admin.site.register(models.MonicaEnvironment, admin.ModelAdmin)
# admin.site.register(models.CentralParameterProvider, admin.ModelAdmin)

# admin.site.register(models.DigitalElevationModel, admin.ModelAdmin)
admin.site.register(models.UserSoilProfile, admin.ModelAdmin)
# admin.site.register(models.SoilProfileLayer, admin.ModelAdmin)

admin.site.register(models.WorkstepMineralFertilisation, BaseUserAdmin)
admin.site.register(models.WorkstepOrganicFertilisation, admin.ModelAdmin)
admin.site.register(models.WorkstepTillage, admin.ModelAdmin)
admin.site.register(models.WorkstepIrrigation, admin.ModelAdmin)
admin.site.register(models.WorkstepSowing, admin.ModelAdmin)
admin.site.register(models.WorkstepHarvest, admin.ModelAdmin)

admin.site.register(models.MonicaSite, MonicaSiteAdmin)
admin.site.register(models.MonicaProject, MonicaProjectAdmin)
admin.site.register(models.Rotation, admin.ModelAdmin)
admin.site.register(models.CropRotation, admin.ModelAdmin)

admin.site.register(models.DWDGridToPointIndices, LeafletGeoAdmin)
