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
from monica import models as monica_models
from buek.models import Buek200

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


class ProjectRegion(models.Model):
    name = models.CharField(max_length=50)
    geom = gis_models.MultiPolygonField(null=True, srid=4326)
    geo_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="drought_userfields")
    name = models.CharField(max_length=255)
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    swn_tool = models.CharField(max_length=16, null=True, blank=True)
    geom_json = PolygonField(null=True)
    comment = models.TextField(null=True, blank=True)
    geom = gis_models.GeometryField(null=True, srid=4326)
    soil_profile_polygon_ids = models.JSONField(null=True, blank=True)
    # TODO check if that is correct or even needed: it is probably BuekSoilProfie and not SoilProfile
    soil_profiles = models.ManyToManyField(
        'SoilProfile',
        through='SoilProfileUserField',
        related_name='drought_userfields',
        blank=True,
    )
    
    weather_grid_points = models.JSONField(null=True, blank=True)
    

    def __str__(self):
        return self.name
    
    def get_intersecting_soil_data(self):
        userfield_geom = self.geom
        print('userfield_geom ', userfield_geom)
        userfield_geom = GEOSGeometry(userfield_geom)

        # Filter Buek objects that intersect with the UserField object's geometry
        intersecting_buek_ids = Buek200.objects.filter(geom__intersects=userfield_geom).values_list('polygon_id', flat=True)
        print('intersecting_buek_ids ', intersecting_buek_ids)
        polygon_json = {'buek_polygon_ids': list(intersecting_buek_ids)}

        print('polygon_json ', polygon_json)
        self.soil_profile_polygon_ids = json.dumps(polygon_json)  # Convert to JSON string
        self.save()

    def get_intersecting_soil_data_raster(self):
        #TODO: today
        userfield_geom = self.geom
        print('userfield_geom ', userfield_geom)
        userfield_geom = GEOSGeometry(userfield_geom)

        # Filter Buek objects that intersect with the UserField object's geometry
        intersecting_buek_ids = Buek.objects.filter(geom__intersects=userfield_geom).values_list('polygon_id', flat=True)
        print('intersecting_buek_ids ', intersecting_buek_ids)
        polygon_json = {'buek_polygon_ids': list(intersecting_buek_ids)}

        print('polygon_json ', polygon_json)
        self.soil_profile_polygon_ids = json.dumps(polygon_json)  # Convert to JSON string
        self.save()

    def get_weather_grid_points(self):
        """
        Get the weather data from the DWD raster/ respectively the point representation in the monica.models.DWDGridToPointIndices class
        that intersects with the UserField object's geometry
        """
        print("get_weather_grid_points")
        userfield_geom = self.geom
        weather_data_indices = monica_models.DWDGridAsPolygon.objects.filter(geom__intersects=userfield_geom)
        
        weather_indices_list = []
        for w in weather_data_indices:
            # print( 'w ', w.id, w.lat_idx, w.lon_idx, w.lat, w.lon, w.is_valid)
            dict = {
                'id': w.id,
                'lat': w.lat,
                'lon': w.lon,
                'lat_idx': w.lat_idx,
                'lon_idx': w.lon_idx,
                'is_valid': w.is_valid,
            }
            weather_indices_list.append(dict)
        weather_indices_json = {'weather_indices': weather_indices_list}
        self.weather_grid_points = json.dumps(weather_indices_json)
        self.save()
        print( 'weather_indices_json ', weather_indices_json)
        return weather_indices_json
    
    def get_centroid(self):
        """
        Get the centroid of the UserField object's geometry
        """
        userfield_geom = self.geom
        userfield_geom = GEOSGeometry(userfield_geom)
        centroid = userfield_geom.centroid
        lat = centroid.y
        lon = centroid.x
        return lon, lat
    
    # # models.py

    # TODO celery task UserField.save
    # def save(self, *args, **kwargs):
    #     from .tasks import process_user_field
    #     super(UserField, self).save(*args, **kwargs) 

    #     # After saving, trigger the Celery task asynchronously
    #     process_user_field.delay(self.pk)

        
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

class UserCalculation(monica_models.ModelSetup):    
    project_name = models.CharField(max_length=255)
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    soil_profile = models.ForeignKey(SoilProfile, on_delete=models.DO_NOTHING, null=True)
    comment = models.TextField(null=True, blank=True)
    calculation_start_date = models.DateField(null=True, blank=True)
    calculation_end_date = models.DateField(null=True, blank=True)
    rotation = models.JSONField(null=True, blank=True)
    calculation = models.JSONField(null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, blank=True)
    # updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    creation_date = models.DateField(auto_now_add=True, blank=True)
    last_modified = models.DateField(auto_now=True, blank=True)
    description = models.TextField(null=True, blank=True)
    user_calculations = models.ManyToManyField(UserCalculation, related_name='user_projects', blank=True)

    def __str__(self):
        return self.name
    
class SwnProject(monica_models.MonicaProject):
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    # lats and lons for the whole area

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
