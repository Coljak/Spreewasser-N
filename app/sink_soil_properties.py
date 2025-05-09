# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class TbSinkSoilProperties(models.Model):
    geom = models.GeometryField(srid=0, blank=True, null=True)
    soil_properties_id = models.BigIntegerField(blank=True, null=True)
    hydraulic_conductivity_1m_rating = models.FloatField(blank=True, null=True)
    hydraulic_conductivity_2m_rating = models.FloatField(blank=True, null=True)
    wet_gras = models.CharField(max_length=50, blank=True, null=True)
    c_wet_gras = models.FloatField(blank=True, null=True)
    c_suit_gw = models.FloatField(blank=True, null=True)
    c_soil_1 = models.FloatField(blank=True, null=True)
    c_soil_2 = models.FloatField(blank=True, null=True)
    c_soil_3 = models.FloatField(blank=True, null=True)
    index_soil_sp = models.FloatField(blank=True, null=True)
    shape_area = models.FloatField(blank=True, null=True)
    c_suit = models.IntegerField(blank=True, null=True)
    nitrate_contamination = models.BooleanField(blank=True, null=True)
    waterlog = models.BooleanField(blank=True, null=True)
    landuse_id = models.BigIntegerField(blank=True, null=True)
    fieldcapacity_id = models.BigIntegerField(blank=True, null=True)
    hydromorphy_id = models.BigIntegerField(blank=True, null=True)
    soil_id = models.BigIntegerField(blank=True, null=True)
    groundwater_distance_id = models.BigIntegerField(blank=True, null=True)
    wet_grassland_id = models.BigIntegerField(blank=True, null=True)
    agricultural_landuse_id = models.BigIntegerField(blank=True, null=True)
    sink_id = models.IntegerField(blank=True, null=True)
    depth = models.FloatField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    index_1 = models.FloatField(blank=True, null=True)
    index_2 = models.FloatField(blank=True, null=True)
    index_3 = models.FloatField(blank=True, null=True)
    land_use_1 = models.CharField(max_length=100, blank=True, null=True)
    land_use_2 = models.CharField(max_length=100, blank=True, null=True)
    land_use_3 = models.CharField(max_length=100, blank=True, null=True)
    land_use_1_percentage = models.FloatField(blank=True, null=True)
    land_use_2_percentage = models.FloatField(blank=True, null=True)
    land_use_3_percentage = models.FloatField(blank=True, null=True)
    index_soil_sink = models.FloatField(blank=True, null=True)
    feasibility_sinks_index = models.FloatField(blank=True, null=True)
    geom_simplified = models.PolygonField(blank=True, null=True)
    index_hydrology = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_sink_soil_properties'
