from django.db import models
from django.contrib.gis.db import models as gis_models

# gw_ezg
class AboveGroundWaters(models.Model):
    uezg_id = models.CharField(max_length=100)
    hapt_ezg = models.CharField(max_length=100, null=True)
    teil_ezg = models.CharField(max_length=100,null=True)
    qru_m3_s = models.FloatField(null=True)
    flaeche_m2 = models.FloatField(null=True)
    bg_id = models.FloatField(null=True)
    geom = gis_models.MultiPolygonField(srid=25833)

    def __str__(self):
        return self.uezg_id

# ezg25 
class BelowGroundWaters(models.Model):
    kennzahl = models.CharField(max_length=16,null=True)
    gewaesser = models.CharField(max_length=60,null=True)
    gew_alias = models.CharField(max_length=60, null=True)
    gew_kennz = models.CharField(max_length=16,null=True)
    beschr_von = models.CharField(max_length=255,null=True)
    beschr_bis = models.CharField(max_length=255,null=True)
    laenge = models.CharField(max_length=20,null=True)
    land = models.CharField(max_length=100,null=True)
    ordnung = models.CharField(max_length=2,null=True)
    fl_art = models.CharField(max_length=2,null=True)
    wrrl_kr = models.CharField(max_length=40,null=True)
    area_qkm = models.FloatField(null=True)
    area_ha = models.FloatField(null=True)
    ezg_id = models.IntegerField(null=True)
    bemerkung = models.CharField(max_length=255,null=True)
    wrrl_fge = models.CharField(max_length=20,null=True)
    wrrl_bg = models.CharField(max_length=40,null=True)
    shape_area = models.FloatField(null=True)
    shape_len = models.FloatField(null=True)
    geom = gis_models.MultiPolygonField(srid=25833)

    def __str__(self):
        return self.kennzahl
    

class UserProject(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    area = gis_models.MultiPolygonField(srid=25833, null=True)

# DE: Injektion/ Qgis _injektion_diss_4326
class OutlineInjection(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Injection')

    def __str__(self):
                return self.name

# DE: Ufernah /Qgis: ufernah_diss_4326
class OutlineSurfaceWater(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Surface Water')

    def __str__(self):
            return self.name

# DE: Versickerung / Qgis: versickerung_diss_4326
class OutlineInfiltration(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Infiltration')  

# DE: Geste??/ Qgis: geste_diss_4326
class OutlineGeste(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Injection')

    def __str__(self):
                return self.name
    

# # DE: Dränung
# class OutlineDrainage(gis_models.Model):
#     name = models.CharField(max_length=64, blank=True, null=True)
#     geom = gis_models.MultiPolygonField('Drainage')

#     def __str__(self):
#                 return self.name


class SoilProperties4326(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326)
    # nitrate_co = models.CharField(max_length=100, null=True)
    # waterloggi = models.CharField(max_length=100, null=True)
    depth_to_groundwater = models.CharField(max_length=100, null=True)
    hydraulic_1m = models.CharField(max_length=100, null=True)
    hydraulic_2m = models.CharField(max_length=100, null=True)
    field_capacity = models.CharField(max_length=100, null=True)
    hydromorph = models.CharField(max_length=100, null=True)
    agriculture = models.CharField(max_length=100, null=True)
    wetness_so = models.CharField(max_length=100, null=True)
    type_of_agriculture = models.CharField(max_length=100, null=True)
    class_land = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)
    nitrate_contamination = models.BooleanField(null=True)
    waterlogging = models.BooleanField(null=True)
    depth_to_groundwater_lower = models.FloatField(null=True)
    depth_to_groundwater_upper = models.FloatField(null=True)


class SinksWithLandUseAndSoilProperties(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)

class SinksWithLandUseAndSoilPropertiesSimplified(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326, default=None)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)


class SinksWithLandUseAndSoilPropertiesAsPoints(models.Model):
    geom = gis_models.PointField(srid=4326)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)