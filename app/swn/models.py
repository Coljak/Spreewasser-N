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
    # winter_summer_crop = models.ForeignKey(WinterSummerCrop, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class ProjectRegion(models.Model):
    name = models.CharField(max_length=50)
    geom = gis_models.MultiPolygonField(null=True)

    def __str__(self):
        return self.name

class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    geom_json = PolygonField(null=True)
    # geom = GeometryField(null=True)
    
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
        self.soil_profile_polygon_ids = polygon_json
        self.save()

        # return intersecting_buek_data
    

    
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

# # Bundesländer
# class NUTS5000_N1(models.Model):
#     #nuts_code_1 = models.CharField(max_length=2)
#     objid = models.CharField(max_length=16)
#     beginn = models.DateField()
#     gf = models.IntegerField()
#     nuts_level = models.IntegerField()
#     nuts_code = models.CharField(max_length=5)
#     nuts_name = models.CharField(max_length=100)
#     geom = gis_models.MultiPolygonField(srid=4326)

#     def __str__(self):
#         return self.nuts_name
    
# #Regierungsbezirke
# class NUTS5000_N2(models.Model):
#     nuts_code_1 = models.ForeignKey(NUTS5000_N1, on_delete=models.CASCADE, default=3)
#     objid = models.CharField(max_length=16)
#     beginn = models.DateField()
#     gf = models.IntegerField()
#     nuts_level = models.IntegerField()
#     nuts_code = models.CharField(max_length=5)
#     nuts_name = models.CharField(max_length=100)
#     geom = gis_models.MultiPolygonField(srid=4326)

#     def __str__(self):
#         return self.nuts_name
    
# class NUTS5000_N3(models.Model):
#     nuts_code_2 = models.ForeignKey(NUTS5000_N2, on_delete=models.CASCADE, default=3)
#     objid = models.CharField(max_length=16)
#     beginn = models.DateField()
#     gf = models.IntegerField()
#     nuts_level = models.IntegerField()
#     nuts_code = models.CharField(max_length=5)
#     nuts_name = models.CharField(max_length=100)
#     geom = gis_models.MultiPolygonField(srid=4326)

#     def __str__(self):
#         return self.nuts_name


    

# ----------BUEK 200 data ------------------------------------------------
class BaseRasterData(models.Model):
    name = models.CharField(max_length=100)
    rast = gis_models.RasterField(srid=4326, null=True, blank=True)
    geotiff = models.FileField(upload_to='geotiffs/')
    

    def __str__(self):
        return self.name
    

from django.contrib.gis.db import models


class Buek(models.Model):
    
    polygon_id = models.BigIntegerField()
    bgl = models.CharField(max_length=80, null=True, blank=True)
    symbol = models.CharField(max_length=80, null=True, blank=True)
    legende = models.CharField(max_length=200, null=True, blank=True)
    hinweis = models.CharField(max_length=91, null=True, blank=True)
    shape_area = models.FloatField()
    shape_leng = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)


    

class BuekData(models.Model):
    
    polygon_id_in_buek = models.IntegerField(null=True, blank=True)
    profile_id_in_polygon = models.IntegerField(null=True, blank=True)
    range_percentage_of_area = models.CharField(max_length=56, null=True, blank=True)
    range_percentage_minimum = models.IntegerField(null=True, blank=True)
    range_percentage_maximum = models.IntegerField(null=True, blank=True)
    avg_range_percentage_of_area = models.IntegerField(null=True, blank=True)
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
    
    def __str__(self):
        return 'soil_profile_all' + str(self.polygon_id_in_buek) + str(self.profile_id_in_polygon)
    


