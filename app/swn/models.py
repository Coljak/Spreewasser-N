"""
Database models.
"""

from email.policy import default
from statistics import mode

from django.db import models
from django.contrib.gis.db import models as gis_models

from django.contrib.gis.db.models.functions import Intersection
from django.db.models import Func, F
from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import GEOSGeometry
from django.core.files import File
# from django_raster import fields as raster_fields
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
#from user.models import User
from django.contrib.auth.models import User
import json

import gettext as _
import datetime
import os

from geo.Geoserver import Geoserver
# from psycopg2 import connect

# db = Pg(dbname=os.environ.get('DB_NAME'), 
#         user=os.environ.get('DB_USER'), 
#         password=os.environ.get('DB_PASS'), 
#         host=os.environ.get('DB_HOST'))


geo = Geoserver(os.environ.get('GEOSERVER_URL'), 
                username=os.environ.get('GEOSERVER_USER'), 
                password=os.environ.get('GEOSERVER_PASS'))



class WinterSummerCrop(models.Model):
    name = models.CharField(max_length=30)
    
class Crop(models.Model):
    name = models.CharField(max_length=64)
    is_winter_crop = models.BooleanField(default=False)
    species_path = models.CharField(max_length=255, null=True, blank=True)
    cultivar_path = models.CharField(max_length=255, null=True, blank=True)
    residue_path = models.CharField(max_length=255, null=True, blank=True)
    # winter_summer_crop = models.ForeignKey(WinterSummerCrop, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class ProjectRegion(models.Model):
    name = models.CharField(max_length=50)
    geom = gis_models.MultiPolygonField(null=True, srid=4326)

    def __str__(self):
        return self.name

class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    swn_tool = models.CharField(max_length=16, null=True, blank=True)
    geom_json = PolygonField(null=True)
    comment = models.TextField(null=True, blank=True)
    geom = gis_models.GeometryField(null=True, srid=4326)
    soil_profile_polygon_ids = models.JSONField(null=True, blank=True)

    soil_profiles = models.ManyToManyField(
        'SoilProfile',
        through='SoilProfileUserField',
        related_name='user_fields',
        blank=True,
    )
    

    def __str__(self):
        return self.name
    
    def get_intersecting_soil_data(self):
        userfield_geom = self.geom
        print( 'userfield_geom ', userfield_geom )
        userfield_geom = GEOSGeometry(userfield_geom)

        # Filter Buek objects that intersect with the UserField object's geometry
        intersecting_buek_ids = Buek.objects.filter(geom__intersects=userfield_geom).values_list('polygon_id', flat=True)
        print( 'intersecting_buek_ids ', intersecting_buek_ids )
        # Get BuekData objects where polygon_id matches the intersecting_buek_ids
        #intersecting_buek_data = BuekData.objects.filter(polygon_id__in=intersecting_buek_ids)
        polygon_json = {'buek_polygon_ids': list(intersecting_buek_ids)}
        
            
        print( 'polygon_json ', polygon_json)
        self.soil_profile_polygon_ids = json.dumps(polygon_json)
        self.save()
        # return intersecting_buek_data
        
# TODO this table is empty-- canlikely be deleted
class SoilProfile(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    horizon_id = models.IntegerField(null=True, blank=True)
    layer_depth = models.IntegerField(null=True, blank=True)
    bulk_density = models.IntegerField(null=True, blank=True)
    raw_density = models.IntegerField(null=True, blank=True)
    soil_organic_carbon = models.FloatField(null=True, blank=True)
    soil_organic_matter = models.IntegerField(null=True, blank=True)
    ph = models.IntegerField(null=True, blank=True)
    ka5_texture_class = models.CharField(max_length=56, null=True, blank=True)
    sand = models.IntegerField(null=True, blank=True)
    clay = models.IntegerField(null=True, blank=True)
    silt = models.IntegerField(null=True, blank=True)
    permanent_wilting_point = models.IntegerField(null=True, blank=True)
    field_capacity = models.IntegerField(null=True, blank=True)
    saturation = models.IntegerField(null=True, blank=True)
    soil_water_conductivity_coefficient = models.IntegerField(null=True, blank=True)
    sceleton = models.IntegerField(null=True, blank=True)
    soil_ammonium = models.IntegerField(null=True, blank=True)
    soil_nitrate = models.IntegerField(null=True, blank=True)
    c_n = models.IntegerField(null=True, blank=True)
    initial_soil_moisture = models.IntegerField(null=True, blank=True)
    layer_description = models.CharField(max_length=56, null=True, blank=True)
    is_in_groundwater = models.IntegerField(null=True, blank=True)
    is_impenetrable = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name

    
class SoilProfileUserField(models.Model):
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    soil_profile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE)
    horizon_id = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name

class UserProject(models.Model):    
    name = models.CharField(max_length=255)
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    soil_profile = models.ForeignKey(SoilProfile, on_delete=models.DO_NOTHING, null=True)
    crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, null=True)
    comment = models.TextField(null=True, blank=True)
    irrigation_input = models.JSONField(null=True, blank=True)
    irrigation_output = models.JSONField(null=True, blank=True)
    calculation_start_date = models.DateField(null=True, blank=True)
    calculation_end_date = models.DateField(null=True, blank=True)
    calculation = models.JSONField(null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name


class GeoData(models.Model):
    name = models.CharField(max_length=56)
    description = models.CharField(max_length=1024, blank=True)
    file = models.FileField(upload_to='geodata', blank=True)
    date = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return self.name
    
# Counties, States, Countries
# Countries
class NUTS0000_N0(models.Model):
    nuts_id = models.CharField(max_length=16)
    gf = models.IntegerField()
    nuts_level = models.IntegerField()
    nuts_code = models.CharField(max_length=5)
    nuts_name = models.CharField(max_length=100)
    name_latin = models.CharField(max_length=100)
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.nuts_name

# Bundesländer
class NUTS5000_N1(models.Model):
    #nuts_code_1 = models.CharField(max_length=2)
    objid = models.CharField(max_length=16)
    beginn = models.DateField()
    gf = models.IntegerField()
    nuts_level = models.IntegerField()
    nuts_code = models.CharField(max_length=5)
    nuts_name = models.CharField(max_length=100)
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.nuts_name
#Regierungsbezirke
class NUTS5000_N2(models.Model):
    nuts_code_1 = models.ForeignKey(NUTS5000_N1, on_delete=models.CASCADE, default=3)
    objid = models.CharField(max_length=16)
    beginn = models.DateField()
    gf = models.IntegerField()
    nuts_level = models.IntegerField()
    nuts_code = models.CharField(max_length=5)
    nuts_name = models.CharField(max_length=100)
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.nuts_name
    
class NUTS5000_N3(models.Model):
    nuts_code_2 = models.ForeignKey(NUTS5000_N2, on_delete=models.CASCADE, default=3)
    objid = models.CharField(max_length=16)
    beginn = models.DateField()
    gf = models.IntegerField()
    nuts_level = models.IntegerField()
    nuts_code = models.CharField(max_length=5)
    nuts_name = models.CharField(max_length=100)
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.nuts_name

# ----------BUEK 200 data ------------------------------------------------



class EcosystemTypes(models.Model):
    label = models.CharField(max_length=255)
    label_de = models.CharField(max_length=255)
    def __str__(self):
        return self.label

class CLCLevel1(models.Model):
    code = models.IntegerField()
    label = models.CharField(max_length=255)
    label_de = models.CharField(max_length=255)
    def __str__(self):
        return self.label
    
class CLCLevel2(models.Model):
    code = models.IntegerField()
    label = models.CharField(max_length=255)
    label_de = models.CharField(max_length=255)
    level1 = models.ForeignKey(CLCLevel1, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.label
    
class CLCLevel3(models.Model):
    code = models.IntegerField()
    label = models.CharField(max_length=255)
    label_de = models.CharField(max_length=255)
    level2 = models.ForeignKey(CLCLevel2, on_delete=models.CASCADE)
    ecosystem_types = models.ForeignKey(EcosystemTypes, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.label
    
class CLC2018(models.Model):
    code = models.IntegerField(null=True, blank=True)
    code_18 = models.CharField(null=True, blank=True)
    code_18_1 = models.IntegerField(null=True, blank=True)
    code_18_2 = models.IntegerField(null=True, blank=True)
    code_18_3 = models.IntegerField(null=True, blank=True)
    clclevel1 = models.ForeignKey(CLCLevel1, on_delete=models.CASCADE, null=True, blank=True)
    clclevel2 = models.ForeignKey(CLCLevel2, on_delete=models.CASCADE, null=True, blank=True)
    clclevel3 = models.ForeignKey(CLCLevel3, on_delete=models.CASCADE, null=True, blank=True)
    objectid = models.IntegerField(null=True, blank=True)
    remark = models.CharField(max_length=255, null=True, blank=True)
    area_ha = models.FloatField(null=True, blank=True)
    clc_id = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    label_de = models.CharField(max_length=255, null=True, blank=True)
    geom = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.label
    
class BuekCapillaryRise(models.Model):
    soil_type = models.CharField(max_length=255, null=True, blank=True)
    ka5textureclass_id = models.IntegerField(null=True, blank=True)
    distance = models.IntegerField(null=True, blank=True)
    capillary_rate = models.FloatField(null=True, blank=True)
    
class BuekBulkDensityClass(models.Model):
    bulk_density_class = models.CharField(null=True, blank=True)
    raw_density_g_per_cm3 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.bulk_density_class

class BuekKa5TextureClass(models.Model):
    ka5_soiltype = models.CharField(max_length=255, null=True, blank=True)
    sand = models.FloatField(null=True, blank=True)
    clay = models.FloatField(null=True, blank=True)
    silt = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.ka5_soiltype
    
class BuekHumusClass(models.Model):
    humus_class = models.CharField(max_length=255, null=True, blank=True)
    corg = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.humus_class
    
class BuekPHClass(models.Model):
    ph_class = models.CharField(max_length=255, null=True, blank=True)
    ph_lower_value = models.FloatField(null=True, blank=True)
    ph_upper_value = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.ph_class


class BuekPolygon(models.Model):
    polygon_id = models.BigIntegerField(primary_key=True)
    bgl = models.CharField(max_length=80, null=True, blank=True)
    symbol = models.CharField(max_length=80, null=True, blank=True)
    legende = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):    
        return 'Polygon ' + str(self.polygon_id)

class Buek(models.Model):  
    id = models.AutoField(primary_key=True)
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    hinweis = models.CharField(max_length=91, null=True, blank=True)
    shape_area = models.FloatField()
    shape_leng = models.FloatField()
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return '  Polygon_id ' + str(self.polygon_id)
    
class BuekVector(models.Model):  
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    hinweis = models.CharField(max_length=91, null=True, blank=True)
    shape_area = models.FloatField()
    shape_leng = models.FloatField()
    geom = gis_models.MultiPolygonField(srid=4326)
    bgl = models.CharField(max_length=80, null=True, blank=True)
    symbol = models.CharField(max_length=80, null=True, blank=True)
    legende = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return '  Polygon_id ' + str(self.polygon_id)

class BuekSoilProfile(models.Model):
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    system_unit = models.CharField(max_length=255, null=True, blank=True)
    area_percenteage = models.IntegerField(null=True, blank=True)
    landusage = models.CharField(max_length=255, null=True, blank=True)
    landusage_corine_code = models.IntegerField(null=True, blank=True)
    soil_profile_no = models.IntegerField(null=True, blank=True)
    corine_code_level_1 = models.IntegerField(null=True, blank=True)
    corine_code_level_2 = models.IntegerField(null=True, blank=True)
    corine_code_level_3 = models.IntegerField(null=True, blank=True)
    clclevel1 = models.ForeignKey(CLCLevel1, on_delete=models.CASCADE, null=True, blank=True)
    clclevel2 = models.ForeignKey(CLCLevel2, on_delete=models.CASCADE, null=True, blank=True)
    clclevel3 = models.ForeignKey(CLCLevel3, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return 'soil_profile ' + str(self.polygon.polygon_id) 

class BuekMissingSoilProfile(models.Model):
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    blatt_no = models.IntegerField(null=True, blank=True)
    le_nr = models.IntegerField(null=True, blank=True)
    info_1 = models.CharField(max_length=255, null=True, blank=True)
    info_2 = models.CharField(max_length=255, null=True, blank=True)
    error_handled = models.BooleanField(default=False)
    legende = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return 'Missing info on ' + str(self.polygon) + ', Blatt no.  ' + str(self.blatt_no) + ', Le-Nr. ' + str(self.le_nr) + '. ' + str(self.info_2) 
                                                                  
class BuekSoilProfileHorizon(models.Model):
    bueksoilprofile = models.ForeignKey(BuekSoilProfile, on_delete=models.CASCADE, null=True, blank=True)
    horizont_nr = models.IntegerField(null=True, blank=True)
    symbol = models.CharField(max_length=255, null=True, blank=True)
    obergrenze_m = models.FloatField(null=True, blank=True)
    untergrenze_m = models.FloatField(null=True, blank=True)
    stratigraphie = models.CharField(max_length=255, null=True, blank=True)
    herkunft = models.CharField(max_length=255, null=True, blank=True)
    geogenese = models.CharField(max_length=255, null=True, blank=True)
    fraktion = models.CharField(max_length=255, null=True, blank=True)
    summe = models.FloatField(null=True, blank=True)
    # bodenart = models.CharField(max_length=255, null=True, blank=True)
    # humus = models.CharField(max_length=255, null=True, blank=True)
    # carbonatgehalt = models.CharField(null=True, blank=True)
    gefuege = models.CharField(max_length=255, null=True, blank=True)
    # trockenrohdichte = models.CharField(max_length=255, null=True, blank=True)
    torfarten = models.CharField(max_length=255, null=True, blank=True)
    # zersetzungsstufe = models.CharField(max_length=255, null=True, blank=True)
    substanzvolumen = models.CharField(max_length=255, null=True, blank=True)
    # bodenaciditaet = models.CharField(max_length=255, null=True, blank=True)
    bulk_density_class = models.ForeignKey(BuekBulkDensityClass, on_delete=models.CASCADE, null=True, blank=True)
    ka5_texture_class = models.ForeignKey(BuekKa5TextureClass, on_delete=models.CASCADE, null=True, blank=True)
    humus_class = models.ForeignKey(BuekHumusClass, on_delete=models.CASCADE, null=True, blank=True)
    ph_class = models.ForeignKey(BuekPHClass, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return super().__str__() + ' soilprofile_id: ' + str(self.bueksoilprofile_id) + ' horizont_nr: ' + str(self.horizont_nr)
    


class CorineLandCover2018(models.Model):
    '''
    CLC 5 classes.
    '''
    label3 = models.CharField(max_length=255, null=True, blank=True)
    code_18 = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.label3 + ' ' + str(self.code_18)
