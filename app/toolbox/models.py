from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from buek.models import CorineLandCover2018
from django.contrib.gis.db.models.functions import Transform
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from datetime import datetime
class ToolboxType(models.Model):
    name_de = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    name_tag = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=255)

    def __str__(self, language='de'):
        return self.name_de if language == 'de' else self.name_en
    



# class DigitalElevationModel10(models.Model):
#      name = models.CharField(max_length=100, null=True, blank=True)
#      elevation = models.FloatField(null=True, blank=True)
#      rast = gis_models.RasterField(srid=25833)
#      extent = gis_models.PolygonField(srid=25833, null=True, blank=True)

# gw_ezg
# TODO: not used - delete or geoserver
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
# TODO: not used - delete or geoserver
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
    

    
class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_userfields")
    name = models.CharField(max_length=255)
    creation_date = models.DateField(blank=True, default=now)
    # TODO is that ever used - it should be a jsonfield.
    geom_json = PolygonField(null=True)
    comment = models.TextField(null=True, blank=True)
    geom = gis_models.GeometryField(null=True, srid=4326)
    geom25833 = gis_models.GeometryField(null=True, srid=25833)
    has_zalf_sinks = models.BooleanField(default=False, null=True, blank=True)
    has_zalf_enlarged_sinks = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_sink = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_gek = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_surface_water = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.geom:
            self.geom25833 = self.geom.transform(25833, clone=True)
            # TODO: 1. 
        super().save(*args, **kwargs)


class ToolboxProject(models.Model):    
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_projects")
    description = models.TextField(null=True, blank=True)
    user_field = models.ForeignKey('UserField', on_delete=models.CASCADE, null=True)
    toolbox_type = models.ForeignKey('ToolboxType', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(blank=True, default=now)
    last_modified = models.DateTimeField(auto_now=True, blank=True)
    project_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def to_json(self):
        """Return project as flat JSON (merge base fields with project_data)."""
        base = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "userField": self.user_field.id if self.user_field else None,
            "toolboxType": self.toolbox_type.name_tag if self.toolbox_type else None,
        }
        # Merge project_data if available
        if self.project_data:
            base.update(self.project_data)
        return base

    
# Gewnet25
# TODO: not used - delete or geoserver
class River(models.Model):
    geom = gis_models.LineStringField()
    name = models.CharField(max_length=255, null=True, blank=True) # w_gn1
    w_gn2 = models.CharField(max_length=255, null=True, blank=True)
    w_gn3 = models.CharField(max_length=255, null=True, blank=True)
    w_gn_lgb = models.CharField(max_length=255, null=True, blank=True)
    w_wdm = models.IntegerField(null=True, blank=True)
    w_ofl = models.IntegerField(null=True, blank=True)
    w_ezg_kl = models.IntegerField(null=True, blank=True)
    w_achse = models.IntegerField(null=True, blank=True)
    w_gwk = models.CharField(max_length=16, null=True, blank=True)
    w_gbk = models.CharField(max_length=16, null=True, blank=True)
    w_sfk_lg = models.CharField(max_length=16, null=True, blank=True)
    w_id = models.IntegerField(null=True, blank=True)

    def to_feature(self):
        """
        Convert the model instance to a GeoJSON feature.
        """
        geometry = json.loads(self.geom.geojson) if self.geom else None
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties":{
                'id': self.id,
                "name": self.name,
            }
        }
    
# WA_CD Kürzel des Koordinierungsraums
class WaterCoordinationEntity(models.Model):
    short = models.CharField(max_length=4, null=True, blank=True)
    name = models.CharField(max_length=64)

# TODO: not used - delete or geoserver
class Lake25(models.Model):
    geom = gis_models.PolygonField()
    geb_kz = models.CharField(max_length=16, null=True, blank=True)
    name = models.CharField(max_length=60, null=True, blank=True)
    objart = models.CharField(max_length=16, null=True, blank=True)
    geo_quelle = models.CharField(max_length=20, null=True, blank=True)
    see_alias = models.CharField(max_length=60, null=True, blank=True)
    stand = models.DateField(null=True, blank=True)
    ms_cd_lw = models.CharField(max_length=24, null=True, blank=True)
    cd_ls = models.CharField(max_length=24, null=True, blank=True)
    wrrl_pg = models.CharField(max_length=20, null=True, blank=True)
    wa_cd = models.CharField(max_length=4, null=True, blank=True) # wa_cd Kürzeldes Koordinierungsraums
    water_coordinatin_entity = models.ForeignKey(WaterCoordinationEntity, on_delete=models.DO_NOTHING, null=True, blank=True)
    genese = models.CharField(max_length=10, null=True, blank=True)
    gis_id = models.IntegerField(null=True, blank=True)
    wrrl = models.IntegerField(null=True, blank=True)
    number_of_swimming_spots = models.IntegerField(null=True, blank=True) # badesee
    quelldat = models.DateField()
    jp_id = models.CharField(max_length=50, null=True, blank=True)
    area_gis = models.FloatField(null=True, blank=True)
    area_gis_h = models.FloatField(null=True, blank=True)
    umfang_gis = models.FloatField(null=True, blank=True)
    see_kz = models.CharField(max_length=24, null=True, blank=True)
    shape_area = models.FloatField(null=True, blank=True)
    shape_len = models.FloatField(null=True, blank=True)

    
    def to_feature(self):
        """
        Convert the model instance to a GeoJSON feature.
        """
        geometry = json.loads(self.geom.geojson) if self.geom else None
        return {
            'type': "Feature",
            'geometry': geometry,
            'properties': {
                'id': self.id,
                'name': self.name,
                'stand': self.stand.isoformat() if self.stand else None,
            }
        }
        



######################### INJECTION ###########################

# TODO: not used 
class SinkWeighting(models.Model):
    """
    User's weighting for a sink project
    """
    general= models.FloatField(default=.2) 
    soil= models.FloatField(default=.8)
    field_capacity = models.FloatField(default=.33)
    hydro_conduct_1m= models.FloatField(default=.33)
    hydro_conduct_2m= models.FloatField(default=.33)
    hydromorphy= models.FloatField(default=.33)
    soil_index= models.FloatField(default=.33)
    grassland_soil_moisture = models.FloatField(default=.25)
    grassland_field_capacity = models.FloatField(default=.25)
    grassland_soil_index = models.FloatField(default=.25)
    grassland_hydromorphy= models.FloatField(default=.25)



# class InfiltrationProject(ToolboxProject):
#     weighting = models.ForeignKey(SinkWeighting, on_delete=models.CASCADE, null=True)


# DE: Injektion/ Qgis _injektion_diss_4326
class OutlineInjection(gis_models.Model):
    """
    Area where injection projects can be evaluated
    """
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



    

### ---- 2024-12-02 ---- ###

class Landuse(models.Model):
    name = models.CharField(max_length=50)
    name_v = models.CharField(max_length=50)
    
    sink_landuse_name = models.CharField(max_length=50, null=True)
    de = models.CharField(max_length=50, null=True, blank=True) # DE: Landnutzung
    en = models.CharField(max_length=50, null=True, blank=True) # EN: Landuse
    
    def __str__(self):
        return self.sink_landuse_name
    
# TODO: not used - delete or geoserver
class LanduseMap(models.Model):
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='landuse_map')
    vegetation = models.BooleanField(null=True, blank=True) 
    geom = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)


class Stream(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    fgw_id = models.IntegerField(null=True, blank=True)  # ArcEGMO-ID des Fließgewässerabschnittes
    # Ökologisch begründete Mindestwasserführung hergeleitet für den 3. BWZ ab 2021 (EZG x MOW / 1000)
    minimum_environmental_flow = models.FloatField(null=True, blank=True) # - m³/s  -777 kein berichtspflichtiger OWK; -999 künstlicher OWK
    shape_length = models.FloatField()
    # id_source = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()
    geom = gis_models.LineStringField(srid=4326, null=True, blank=True)
    geom25833 = gis_models.MultiLineStringField(srid=25833, null=True, blank=True)

    def to_json(self):
        return {
                'id': self.id,
                'name': self.name,
                'fgw_id': self.fgw_id,
                'shape_length': round(self.shape_length, 2),
                'minimum_environmental_flow': self.minimum_environmental_flow,
                'min_surplus_volume': round(self.min_surplus_volume, 2),
                'mean_surplus_volume': round(self.mean_surplus_volume, 2),
                'max_surplus_volume': round(self.max_surplus_volume, 2),
                'plus_days': self.plus_days
        }
    
    def to_feature(self):
        geometry = json.loads(self.geom.geojson)
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
        

class Lake(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    fgw_id = models.IntegerField(null=True, blank=True)  # ArcEGMO-ID des Fließgewässerabschnittes
    # Ökologisch begründete Mindestwasserführung hergeleitet für den 3. BWZ ab 2021 (EZG x MOW / 1000)
    minimum_environmental_flow = models.FloatField(null=True, blank=True) # - m³/s  -777 kein berichtspflichtiger OWK; -999 künstlicher OWK
    geom = gis_models.MultiPolygonField(srid=4326)
    geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    shape_length = models.FloatField()
    shape_area = models.FloatField()
    # id_lake = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()
    simple_geom = gis_models.PolygonField(srid=4326, null=True, blank=True)

    def to_json(self):
        return {
                'id': self.id,
                'name': self.name,
                'fgw_id': self.fgw_id,
                'shape_length': round(self.shape_length, 2),
                'shape_area': round(self.shape_area, 2),
                'minimum_environmental_flow': self.minimum_environmental_flow,
                'min_surplus_volume': round(self.min_surplus_volume, 2),
                'mean_surplus_volume': round(self.mean_surplus_volume, 2),
                'max_surplus_volume': round(self.max_surplus_volume, 2),
                'plus_days': self.plus_days
        }
    
    def to_feature(self):
        geometry = json.loads(self.geom.geojson)
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

class Sink(models.Model):
    #id = models.IntegerField(primary_key=True)
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)

    geom_simplified = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_proportions = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    landuse_1 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse_1')
    land_use_2 = models.CharField(max_length=100, null=True)
    landuse_2 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse_2')
    land_use_3 = models.CharField(max_length=100, null=True)
    landuse_3 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse_3')
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    soil_points = models.CharField(max_length=16, null=True, blank=True) # number of soil points
    index_feasibility = models.FloatField(null=True) # Eval of soil points
    hydrogeology_text = models.CharField(max_length=255, null=True, blank=True) # related table
    aquifer = models.ForeignKey('Aquifer', on_delete=models.DO_NOTHING, null=True, blank=True)
    index_hydrogeology = models.FloatField(null=True, blank=True)


    def to_json(self, language='de'):

        landuse_1 = getattr(self.landuse_1, language, None)
        landuse_2 = getattr(self.landuse_2, language, '-')
        landuse_3 = getattr(self.landuse_3, language, '-')
            

        landuse = landuse_1
        if self.landuse_2:
            landuse += landuse_2
            if self.landuse_3:
                landuse += landuse_3

        return {
            "id": self.id,
            "depth": round(self.depth, 2),
            "area": round(self.area, 2),
            "volume": round(self.volume, 2),
            "index_proportions": round(self.index_proportions * 100, 1),
            "index_soil": round(self.index_soil * 100, 1),
            "land_use": landuse,
            "land_use_1": landuse_1,
            "land_use_2": landuse_2,
            "land_use_3": landuse_3,
            "index_soil": round(self.index_soil * 100, 1),
            "soil_points": self.soil_points,
            "index_feasibility": round(self.index_feasibility * 100, 1) if self.index_feasibility else "-",
            "hydrogeology": getattr(self.aquifer, f'name_{language}', None),
            "index_hydrogeology": round(self.index_hydrogeology *100, 1) if self.index_hydrogeology else None,
        }
    

    def to_point_feature(self, language='de'):      
        geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    
    def to_feature(self, language='de'):      
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    



class EnlargedSink(models.Model): 
    # id = models.IntegerField(primary_key=True) # former fid_sink
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    geom_simplified = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    nat_length = models.FloatField(null=True)
    por_length = models.FloatField(null=True)
    con_length = models.FloatField(null=True)
    constructed_sink = models.BooleanField(null=True, default=False)
    volume = models.FloatField(null=True)
    volume_construction_barrier = models.FloatField(null=True)
    volume_gained =  models.FloatField(null=True)
    construction_efficiciency = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_proportions = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    landuse_1 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_1')
    land_use_2 = models.CharField(max_length=100, null=True)
    landuse_2 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_2')
    land_use_3 = models.CharField(max_length=100, null=True)
    landuse_3 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_3')
    land_use_4 = models.CharField(max_length=100, null=True)
    landuse_4 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_4')
    land_use_4_fk = models.IntegerField(null=True, blank=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    land_use_4_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    soil_points = models.CharField(max_length=16, null=True, blank=True)
    index_feasibility = models.FloatField(null=True)
    hydrogeology_text = models.CharField(max_length=255, null=True, blank=True) # related table
    aquifer = models.ForeignKey('Aquifer', on_delete=models.DO_NOTHING, null=True, blank=True) # related table
    index_hydrogeology = models.FloatField(null=True, blank=True) # related table
# Intersect of LandusMap and Sink

    
    def to_json(self, language='de'):

        landuse_1 = getattr(self.landuse_1, language, None)
        landuse_2 = getattr(self.landuse_2, language, None) if self.landuse_2 else '-'
        landuse_3 = getattr(self.landuse_3, language, None) if self.landuse_3 else '-'
        landuse_4 = getattr(self.landuse_4, language, None) if self.landuse_4 else '-'
            

        landuse = landuse_1
        if self.landuse_2:
            landuse += landuse_2
            if self.landuse_3:
                landuse += landuse_3
                if self.landuse_4:
                    landuse += landuse_4

        return {
            "id": self.id,
            "depth": round(self.depth, 2),
            "area": round(self.area, 2),
            "volume": round(self.volume, 2),
            "index_proportions": round(self.index_proportions * 100, 1),
            "index_soil": round(self.index_soil * 100, 1),
            "land_use": landuse,
            "land_use_1": landuse_1,
            "land_use_2": landuse_2,
            "land_use_3": landuse_3,
            "land_use_4": landuse_4,
            "index_soil": round(self.index_soil * 100, 1),
            "soil_points": self.soil_points,
            "index_feasibility": round(self.index_feasibility * 100, 1) if self.index_feasibility else "-",
            "hydrogeology": getattr(self.aquifer, f'name_{language}', None),
            "index_hydrogeology": round(self.index_hydrogeology *100, 1) if self.index_hydrogeology else None,
        }
    
     
    def to_point_feature(self, language='de'):      
        geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    
    def to_feature(self, language='de'):      
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    

class Aquifer(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    name_de = models.CharField(max_length=255, null=True, blank=True)
    name_en = models.CharField(max_length=255, null=True, blank=True)

# Intersect of LandusMap and EnlargedSink -- not in use
class LanduseSink(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    sink = models.ForeignKey(Sink, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse')
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)
    total_area = models.FloatField(null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    area_of_total = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True)

    def __str__(self):
        return f"{self.sink.id} - {self.landuse.name} ({self.percentage}%)"
    
# Intersect of LandusMap and EnlargedSink -- not in use
class LanduseEnlargedSink(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse')
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)
    total_area = models.FloatField(null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    area_of_total = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True)

    def __str__(self):
        return f"{self.sink.id} - {self.landuse.name} ({self.percentage}%)"

class Feasibility(models.Model): # soilstuff
    # (100 - Ackerzahl) / 100 = index_feasibility 
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)
    veg_fe = models.CharField(max_length=100, null=True) # delete ??
    vegetation = models.BooleanField(null=True, default=False) 
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)
    soil_quality_index = models.IntegerField(null=True) # Ackerzahl
    index_feasibility = models.FloatField(null=True)

# TODO not used - geoserver?
class Hydrogeology(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50, null=True)
    aquifer = models.CharField(max_length=150, null=True)
    index = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()

# TODO not used - geoserver?
class HydrogeologySinks(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50)
    aquifer = models.CharField(max_length=150)
    sink = models.ForeignKey(Sink, on_delete=models.DO_NOTHING, null=True)
    index_sink = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

# TODO not used - geoserver?
class HydrogeologyEnlargedSinks(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50)
    aquifer = models.CharField(max_length=150)
    index_sink = models.FloatField(null=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING, null=True) # fid_sink

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

class EnlargedSinkEmbankment(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    centroid4326 = gis_models.PointField(srid=4326, null=True, blank=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='sink_embankment') 

    fid_sink = models.IntegerField()
    height = models.FloatField()
    plat_width = models.FloatField()
    volume = models.FloatField()

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

    def to_feature(self):
        """
        Convert the model instance to a GeoJSON feature.
        """
        return {
            "type": "Feature",
            "geometry": json.loads(self.geom4326.geojson),
            "properties": {
                "fid_sink": self.fid_sink,
                "height": self.height,
                "plat_width": self.plat_width,
                "volume": self.volume,
            }
        }


class GroundWaterDistanceClass(models.Model):
    upper_limit = models.FloatField(null=True)
    lower_limit = models.FloatField(null=True)
    class_name = models.CharField(max_length=50, null=True)
    rating_index = models.FloatField()

    def __str__(self):
        limits = []
        if self.upper_limit:
            limits.append(f"> {self.upper_limit} m")
        if self.lower_limit:
            limits.append(f"< {self.lower_limit} m")
        return ", ".join(limits) if limits else "no data"

class FieldCapacity(models.Model):
    MIN_VOL_CHOICES = [
        (None, "No Data"),
        (0, "< 13 vol.%"),
        (13, "< 26 vol.%"),
        (26, "< 39 vol.%"),
        (39, "< 52 vol.%"),
        (52, "> 52 vol.%"),
    ]
    MAX_VOL_CHOICES = [
        (None, "No Data"),
        (52, "> 52 vol.%"),
    ]

    PARTIAL_MIN_VOL_CHOICES = [
        (None, "No Partial Data"),
        (13, "< 13 vol.%"),
        (26, "< 26 vol.%"),
        (39, "< 39 vol.%"),
        (52, "< 52 vol.%"),
    ]

    PARTIAL_MAX_VOL_CHOICES = [
        (None, "No Partial Data"),
        (13, "> 13 vol.%"),
        (26, "> 26 vol.%"),
        (39, "> 39 vol.%"),
        (52, "> 52 vol.%"),
    ]

    min_vol = models.IntegerField(
        choices=MIN_VOL_CHOICES, null=True, blank=True, help_text="Minimum soil volume percentage"
    )
    max_vol = models.IntegerField(
        choices=MAX_VOL_CHOICES, null=True, blank=True, help_text="Maximum soil volume percentage"
    )
    partially_min_vol = models.IntegerField(
        choices=PARTIAL_MIN_VOL_CHOICES, null=True, blank=True, help_text="Partially lower than"
    )
    partially_max_vol = models.IntegerField(
        choices=PARTIAL_MAX_VOL_CHOICES, null=True, blank=True, help_text="Partially greater than"
    )
    lack_of_data = models.BooleanField(default=False)
    rating_index = models.FloatField()

    def __str__(self):
        conditions = []
        if self.min_vol is not None:
            conditions.append(f"< {self.min_vol} vol.%")
        elif self.max_vol is not None:
            conditions.append(f"> {self.max_vol} vol.%")
        if self.partially_min_vol is not None:
            conditions.append(f"partially < {self.partially_min_vol} vol.%")
        if self.partially_max_vol is not None:
            conditions.append(f"partially > {self.partially_max_vol} vol.%")
        if self.lack_of_data:
            conditions.append("partial lack of data")
        return ", ".join(conditions) if conditions else "no data"

class Hydromorphy(models.Model):
    name = models.CharField(max_length=50)
    rating_index = models.FloatField()

class SoilTexture(models.Model):
    name = models.CharField(max_length=50)
    rating_index = models.FloatField()

class AgriculturalLanduse(models.Model):
    name = models.CharField(max_length=50)

class WetGrassland(models.Model):
    name = models.CharField(max_length=50)
    rating_index = models.FloatField()


class SoilProperties(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)   
    nitrate_contamination = models.BooleanField(default=False) # Factor for Index 1
    waterlog = models.BooleanField(default=False) # Factor for Index 1
    groundwater_distance = models.ForeignKey(GroundWaterDistanceClass, on_delete=models.DO_NOTHING, null=True) # Factor for Index 1 .ratig_index
    hydraulic_conductivity_1m_rating = models.FloatField() # Factor for Index 2.1
    hydraulic_conductivity_2m_rating = models.FloatField() # Factor for Index 2.1
    fieldcapacity = models.ForeignKey(FieldCapacity, on_delete=models.DO_NOTHING, null=True) # Factor for Index 2.1, 2.2 and 2.3 .rating_index
    hydromorphy = models.ForeignKey(Hydromorphy, on_delete=models.DO_NOTHING, null=True) # Factor for Index 2.2 and 2.3 .rating_index
    soil_texture = models.ForeignKey(SoilTexture, on_delete=models.DO_NOTHING, null=True) # Factor for Index 2.2 and 2.3 .rating_index
    wet_grassland = models.ForeignKey(WetGrassland, on_delete=models.DO_NOTHING, null=True)# Factor for Index 2.3 .rating_index
    c_suit = models.IntegerField() # Index 1 without gw???? 0 or 1
    c_suit_gw = models.FloatField() # Index 1 with depth_gw
    c_soil_1 = models.FloatField() # Index 2.1
    c_soil_2 = models.FloatField() # Index 2.2
    c_soil_3 = models.FloatField() # Index 2.3
    index_soil = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()
    agricultural_landuse = models.ForeignKey(AgriculturalLanduse, on_delete=models.DO_NOTHING, null=True) # TODO !!!! THIS IS ANOTHER CATEGORY INTRODUCED!!! WHY???
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)
 
# Intersection of SoilProperties and Sink
class SinkSoilProperties(models.Model):
    geom = gis_models.GeometryField(srid=4326, blank=True, null=True)
    partial_sink_area = models.FloatField(blank=True, null=True)
    percent_of_total_area = models.FloatField(blank=True, null=True)
    soil_properties = models.ForeignKey(SoilProperties, on_delete=models.DO_NOTHING, blank=True, null=True)
    sink = models.ForeignKey(Sink, on_delete=models.DO_NOTHING, null=True, related_name='sink_soil_properties')   
    sink_fid = models.IntegerField(null=True, blank=True)  # former fid_sink
# Intersection of SoilProperties and EnlargedSink
class EnlargedSinkSoilProperties(models.Model):
    geom = gis_models.GeometryField(srid=4326, blank=True, null=True)
    partial_sink_area = models.FloatField(blank=True, null=True)
    percent_of_total_area = models.FloatField(blank=True, null=True)
    soil_properties = models.ForeignKey(SoilProperties, on_delete=models.DO_NOTHING, blank=True, null=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING,  blank=True, null=True, related_name='enlarged_sink_soil_properties')


####################### SIEKER ########################


class SiekerLargeLake(models.Model):
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    stand = models.DateField(null=True, blank=True)
    wrrl_pg = models.CharField(max_length=100, null=True, blank=True)
    genese = models.CharField(max_length=100, null=True, blank=True)
    wrrl = models.IntegerField(null=True, blank=True)
    number_of_swimming_spots = models.IntegerField(null=True, blank=True) # Badesee
    quelldat = models.DateField(null=True, blank=True)
    area_m2 = models.IntegerField(null=True, blank=True)
    area_ha = models.FloatField(null=True, blank=True)
    vol_mio_m3 = models.FloatField(null=True, blank=True)
    einzugsgebiet_km2 = models.FloatField(null=True, blank=True) # Einzugsgebiet in km²
    d_max_m = models.IntegerField(null=True, blank=True) # max depth of lake in m
    verweilt = models.CharField(max_length=100, null=True, blank=True)
    t_cm_per_a = models.FloatField(null=True, blank=True) # annual trend of next level
    seetyp = models.IntegerField(null=True, blank=True)
    seetyp_txt = models.CharField(max_length=100, null=True, blank=True)

    def to_json(self, language='de'):
        if (language == 'de'):
            stand = datetime.strftime(self.stand, '%d.%m.%Y')
        else:
            stand = self.stand.isoformat()
            
        return {
                'id': self.id,
                "name": self.name,
                "stand": stand,
                "wrrl_pg": self.wrrl_pg,
                "genese": self.genese,
                "wrrl": self.wrrl,
                "number_of_swimming_spots": '-' if self.number_of_swimming_spots == -1 else self.number_of_swimming_spots,
                "quelldat": self.quelldat.isoformat() if self.quelldat else None,
                "area_m2": round(self.area_m2) if self.area_m2 else None,
                "area_ha": round(self.area_ha, 1) if self.area_ha else None,
                "vol_mio_m3": round(self.vol_mio_m3) if self.vol_mio_m3 else None,
                "einzugsgebiet_km2": self.einzugsgebiet_km2,
                "d_max_m": self.d_max_m,
                "verweilt": self.verweilt,
                "t_cm_per_a": self.t_cm_per_a,
                "seetyp": self.seetyp,
                "seetyp_txt": self.seetyp_txt
            }

    def to_feature(self, language='de'):
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }


                               

class SiekerWaterLevel(models.Model):
    geom25833 = gis_models.PointField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PointField(srid=4326, null=True, blank=True)
    messstelle = models.CharField(max_length=100, null=True, blank=True)
    t_d = models.IntegerField(null=True, blank=True)  
    t_a = models.FloatField(null=True, blank=True)
    # startdatum = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    # enddatum = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    min_cm = models.IntegerField(null=True, blank=True)  
    max_cm = models.IntegerField(null=True, blank=True)  
    mw_10_19 = models.FloatField(null=True, blank=True)  
    mw_90_99 = models.FloatField(null=True, blank=True)  
    stdev_cm = models.FloatField(null=True, blank=True)  
    twenty_yr_trend = models.FloatField(null=True, blank=True)
    pkz = models.CharField(max_length=100, null=True, blank=True)
    pegelname = models.CharField(max_length=100, null=True, blank=True)
    gewaesser = models.CharField(max_length=100, null=True, blank=True)
    pegelart = models.CharField(max_length=100, null=True, blank=True)  
    mess_w = models.CharField(max_length=100, null=True, blank=True)
    mess_q = models.CharField(max_length=100, null=True, blank=True)
    soll_w = models.CharField(max_length=100, null=True, blank=True)
    soll_q = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    hwmp = models.IntegerField(null=True, blank=True)  
    dgjp = models.IntegerField(null=True, blank=True)  
    gwk = models.CharField(max_length=100, null=True, blank=True)
    gbk = models.CharField(max_length=100, null=True, blank=True)
    a_ezg = models.FloatField(null=True, blank=True)
    bemerkung = models.CharField(max_length=100, null=True, blank=True)
    anfrage = models.CharField(max_length=100, null=True, blank=True)
    stat = models.CharField(max_length=100, null=True, blank=True)
    ent_quell = models.IntegerField(null=True, blank=True)  
    ent_muend = models.IntegerField(null=True, blank=True)  
    diff_cm = models.IntegerField(null=True, blank=True)  
    bilddatei = models.CharField(max_length=100, null=True, blank=True)

    def to_json(self, language='de'):
        if (language == 'de'):
            start_date = datetime.strftime(self.start_date, '%d.%m.%Y')
            end_date = datetime.strftime(self.end_date, '%d.%m.%Y')
        else:
            start_date = self.start_date.isoformat()
            end_date = self.end_date.isoformat()
        return {
            "messstelle": self.messstelle,
            "t_d": self.t_d,
            "t_a": round(self.t_a),
            "period": f"{start_date} - {end_date}",
            "min_cm": self.min_cm,
            "max_cm": self.max_cm,
            "mw_10_19": self.mw_10_19,
            "mw_90_99": self.mw_90_99,
            "stdev_cm": self.stdev_cm,
            "twenty_yr_trend": self.twenty_yr_trend,
            "pkz": self.pkz,
            "pegelname": self.pegelname,
            "gewaesser": self.gewaesser,
            "pegelart": self.pegelart,
            "mess_w": self.mess_w,
            "mess_q": self.mess_q,
            "soll_w": self.soll_w,
            "soll_q": self.soll_q,
            "region": self.region,
            "hwmp": self.hwmp,
            "dgjp": self.dgjp,
            "gwk": self.gwk,
            "gbk": self.gbk,
            "a_ezg": self.a_ezg,
            "bemerkung": self.bemerkung,
            "anfrage": self.anfrage,
            "stat": self.stat,
            "ent_quell": self.ent_quell,
            "ent_muend": self.ent_muend,
            "diff_cm": self.diff_cm,
        }

    def to_feature(self, language='de'):
        
        geometry = json.loads(self.geom4326.geojson) if self.geom4326 else None
        properties = self.to_json(language)
        return {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }



class SiekerSink(models.Model):
    geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    geom_single = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom_remaining = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    fid = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    depth = models.FloatField(null=True, blank=True)
    max_elevation = models.FloatField(null=True, blank=True)
    min_elevation = models.FloatField(null=True, blank=True)
    urbanarea = models.CharField(max_length=100, null=True, blank=True)
    urbanarea_percent = models.FloatField(null=True, blank=True)
    wetlands = models.CharField(max_length=100, null=True, blank=True)
    wetlands_percent = models.FloatField(null=True, blank=True)
    avg_depth = models.FloatField(null=True, blank=True)
    distance_t = models.FloatField(null=True, blank=True)
    dist_lake = models.CharField(max_length=100, null=True, blank=True)
    umsetzbark = models.CharField(max_length=100, null=True, blank=True)
    index_feasibility = models.FloatField(null=True, blank=True)
    waterdist = models.CharField(max_length=100, null=True, blank=True)

    def to_json(self, language='de'):
        return {
                "id": self.id,
                "depth": round(self.depth, 2),
                "area": round(self.area, 1),
                "volume": round(self.volume, 1),
                "avg_depth": round(self.avg_depth, 1),
                "max_elevation": round(self.max_elevation, 1),
                "min_elevation": round(self.min_elevation, 1),
                "urbanarea_percent": self.urbanarea_percent,
                "wetlands_percent": self.wetlands_percent,
                "distance_t": self.distance_t,
                "dist_lake": self.dist_lake,
                "waterdist": self.waterdist,
                "umsetzbark": self.umsetzbark,
                "index_feasibility": self.index_feasibility
               
            }
    
    def to_point_feature(self, language='de'):      
        geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    
    def to_feature(self, language='de'):  
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
class LanduseCLC2018(models.Model):
    geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    geom_single = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    fid = models.FloatField(null=True, blank=True)
    objectid= models.FloatField(null=True, blank=True)
    clc18 = models.CharField(max_length=50, null=True, blank=True)  # CLC code
    shape_leng = models.FloatField(null=True, blank=True)
    shape_area = models.FloatField(null=True, blank=True)
    name_de = models.CharField(max_length=150, null=True, blank=True)


#GEK_Rueckhalteräume

class GekDocument(models.Model):
    link = models.URLField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    year_of_publication = models.IntegerField(null=True, blank=True)

class GekRetention(models.Model):
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid4326 = gis_models.PointField(srid=4326, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    current_landusage = models.CharField(max_length=100, null=True, blank=True) # derz_nutzu
    quelle_1 = models.CharField(max_length=100, null=True, blank=True) # obsolete, always 'GEK'
    quelle_2 = models.CharField(max_length=100, null=True, blank=True)
    association = models.CharField(max_length=100, null=True, blank=True)
    
    planning_segment = models.CharField(max_length=100, null=True, blank=True) # Planungsabschnitt entlang des Gewässers
    hrsg = models.CharField(max_length=100, null=True, blank=True) # 'Bundesanstalt für Gewässerkunde'
    gek_document = models.ForeignKey('GekDocument', on_delete=models.CASCADE, null=True, blank=True, related_name='retention_areas')
    number_of_measures = models.IntegerField(null=True, blank=True)
    datum_zugr = models.CharField(max_length=100, null=True, blank=True) # not necessary

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quelle_1": self.quelle_1,
            "quelle_2": self.quelle_2,
            "current_landusage": self.current_landusage,
            "association": self.association,
            "planning_segment": self.planning_segment,
            "hrsg": self.hrsg,
            "document": self.gek_document.link,
            "number_of_measures": self.number_of_measures
        }
    
    def to_feature(self):
        geometry = json.loads(self.geom4326.geojson) if self.geom4326 else None
        properties = self.to_dict()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }


# m:n table 
class GekLanduse(models.Model):
    gek_retention = models.ForeignKey(GekRetention, on_delete=models.CASCADE, related_name='landuses')
    current_landuse = models.CharField(max_length=100, null=True, blank=True) # derz_nutzu Original Data!
    first_two_clc_digits = models.CharField(max_length=2, null=True, blank=True) # CLC code
    clc_landuse = models.ForeignKey(CorineLandCover2018, on_delete=models.CASCADE, null=True, blank=True, related_name='gek_landuses')
    area_total = models.FloatField(null=True, blank=True) # Total area of the landuse in m²
    area_of_landuse = models.FloatField(null=True, blank=True) # Area of the landuse in m²
    area_percentage = models.FloatField(null=True, blank=True) # Percentage of the landuse area compared to the total area
    
    def __str__(self):
        return f"{self.current_landuse} ({self.first_two_clc_digits})"


class GekPriority(models.Model):
    description_de = models.CharField(max_length=255, null=True, blank=True)
    description_en = models.CharField(max_length=255, null=True, blank=True)
    priority_level = models.IntegerField(null=True, blank=True)  # 1, 2, or 3

    def __str__(self):
        return f"{self.description_de} (Priority Level: {self.priority_level})"


class GEKMeasures(models.Model):
    description_de = models.CharField(max_length=255, null=True, blank=True)

class GekRetentionMeasure(models.Model):
    gek_retention = models.ForeignKey(GekRetention, on_delete=models.CASCADE, related_name='measures')
    gek_measure = models.ForeignKey(GEKMeasures, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True) # anz
    description_de = models.CharField(max_length=255, null=True, blank=True)
    priority = models.ForeignKey(GekPriority, on_delete=models.CASCADE, null=True, blank=True, related_name='measures')
    kosten = models.CharField(max_length=100, null=True, blank=True)
    costs_2013 = models.IntegerField(null=True, blank=True)  # Kosten in Euro
    costs = models.IntegerField(null=True, blank=True) # Adjusted for 2025
    measure_number = models.IntegerField(null=True, blank=True)  # Maßnahme Nummer (2 in 2MNT_ID)

    def to_dict(self, language='de'):
        return {
            "id": self.id,
            "gek_measure": self.gek_measure.description_de if language == 'de' else self.gek_measure.description_en,
            "quantity": self.quantity,
            "description": getattr(self, f'description_{language}', None),
            "priority": self.priority.id if self.priority else None,
            "kosten": self.kosten,
            "costs": self.costs,
            "measure_number": self.measure_number
            }
class WetlandFeasibility(models.Model):
    name_de = models.CharField(max_length=32, blank=True, null=True)
    name_en = models.CharField(max_length=32, blank=True, null=True)
    index = models.FloatField(blank=True, null=True)

# Historische >Rückhalteräume
class HistoricalWetlands(models.Model):
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    current_landusage = models.CharField(max_length=100, null=True, blank=True)
    source_1 = models.CharField(max_length=100, null=True, blank=True)
    source_2 = models.CharField(max_length=100, null=True, blank=True)
    source_3 = models.CharField(max_length=100, null=True, blank=True)
    association = models.CharField(max_length=100, null=True, blank=True)
    document_1 = models.CharField(max_length=100, null=True, blank=True)
    area = models.IntegerField(null=True, blank=True) # m² 
    water_connection = models.CharField(max_length=100, null=True, blank=True)
    feucht_per = models.FloatField(null=True, blank=True)
    # feasibility = models.CharField(max_length=100, null=True, blank=True)
    # index_feasibility = models.IntegerField(null=True, blank=True)
    feasibility = models.ForeignKey(WetlandFeasibility, blank=True, null=True, on_delete=models.CASCADE)

    def to_json(self, language='de'):
        return {
                "id": self.id,
                "name": self.name,
                "comment": self.comment,
                "current_landusage": self.current_landusage,
                "association": self.association,
                "source_1": self.source_1,
                "source_2": self.source_2,
                "source_3": self.source_3,
                "feasibility": getattr(self.feasibility, f'name_{language}', None),
                "index_feasibility": self.feasibility.index,
            }
    
    def to_feature(self):
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }


# # TODO delete ??
# class SinkDifference(models.Model):
#     geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
#     geom_single = gis_models.PolygonField(srid=25833, null=True, blank=True)
#     geom_remaining = gis_models.PolygonField(srid=25833, null=True, blank=True)
#     geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
#     fid = models.FloatField(null=True, blank=True)
#     volume = models.FloatField(null=True, blank=True)
#     area = models.FloatField(null=True, blank=True)
#     sink_depth = models.FloatField(null=True, blank=True)
#     max_elevation = models.FloatField(null=True, blank=True)
#     min_elevation = models.FloatField(null=True, blank=True)
#     urbanarea = models.CharField(max_length=100, null=True, blank=True)
#     urbanarea_percent = models.FloatField(null=True, blank=True)
#     wetlands = models.CharField(max_length=100, null=True, blank=True)
#     wetlands_percent = models.FloatField(null=True, blank=True)
#     avg_depth = models.FloatField(null=True, blank=True)
#     distance_t = models.FloatField(null=True, blank=True)
#     dist_lake = models.CharField(max_length=100, null=True, blank=True)
#     umsetzbark = models.CharField(max_length=100, null=True, blank=True)
#     waterdist = models.CharField(max_length=100, null=True, blank=True)

    

def default_legend_labels():
    """
    This Dictionary sets the labels on a map legend. The number value is the one set in color_by_index.
    """
    return {'header': '', 'label_by_value': ''}

class LeafletLegend(models.Model):
    header_de = models.CharField(max_length=64)
    header_en = models.CharField(max_length=64, null=True, blank=True)

    def to_dict(self, language='de'):
        
        return {
            'header': getattr(self, f'header_{language}'),
            'grades': [g.value for g in self.grades.all().order_by('order_position')],
            'gradientLabels': [getattr(g, f'label_{language}') for g in self.grades.all().order_by('order_position')],
        }

class LegendGrade(models.Model):
    leaflet_legend = models.ForeignKey(LeafletLegend, on_delete=models.CASCADE, related_name="grades")
    value = models.FloatField()
    label_de = models.CharField(max_length=64)
    label_en = models.CharField(max_length=64, null=True, blank=True)
    order_position = models.PositiveIntegerField(default=0)

class DataInfo(models.Model):
    data_type = models.CharField(max_length=255)  # e.g. 'sieker_gek'
    feature_color = models.CharField(max_length=255, default="var(--bs-secondary)") # string defining the (bootstrap) color
    class_name = models.CharField(max_length=255)
    feature_type = models.CharField(max_length=255, default="polygon")
    table_caption = models.CharField(max_length=255)
    popup_header = models.CharField(max_length=255, null=True, blank=True)  # e.g. "name"
    marker_cluster = models.BooleanField(default=False, null=True, blank=True)
    color_by_index = models.CharField(default=None, max_length=32, null=True, blank=True)
    # a legend is only created if color_by_index is not None 
    legend = models.ForeignKey(LeafletLegend, on_delete=models.CASCADE, default=None, null=True, blank=True)
    # icon path is relevant for point values, that have a custom pin icon
    icon_path = models.CharField(max_length=256, null=True, blank=True)

    def to_dict(self, language="de"):
        dict = {
            "dataType": self.data_type,
            "featureColor": self.feature_color,
            "className": self.class_name,
            "featureType": self.feature_type,
            "tableCaption": self.table_caption,
            "popUp": {"header": self.popup_header},
            "properties": [p.to_dict(language) for p in self.properties.all().order_by('order_position')],
            "tableLength": self.properties.filter(table=True).count(),
            
        }
        if self.color_by_index:
            dict.update({"colorByIndex": self.color_by_index})
        if self.icon_path:
            dict.update({"pinIconPath": self.icon_path})
        if self.legend:
            dict.update({"legendSettings": self.legend.to_dict(language)})

        return dict


class DataInfoProperty(models.Model):
    order_position = models.SmallIntegerField(null=True, blank=True)
    data_info = models.ForeignKey(DataInfo, on_delete=models.CASCADE, related_name="properties")
    popup = models.BooleanField(default=True)
    table = models.BooleanField(default=True)
    title_de = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=16, null=True, blank=True)
    value_name = models.CharField(max_length=255)  # e.g. "name" or "gek_document__link"
    href = models.BooleanField(default=False)

    def to_dict(self, language="de"):
        return {
            "popUp": self.popup,
            "table": self.table,
            "title": getattr(self, f'title_{language}', None),
            "valueName": self.value_name,
            "unit": self.unit,
            "href": self.href,
        }


## TU Berlin
class Station(models.Model):
    name = models.CharField(max_length=50)
    waterbody = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.PointField(srid=25833, null=True, blank=True)
    data_provider = models.CharField(max_length=32)
    absolute_elevation_of_sensor_m = models.FloatField(null=True, blank=True)
    gauge_zero = models.FloatField(null=True, blank=True)
    station_number = models.IntegerField(null=True, blank=True)

# TODO: what is this? amount m³/s. The data is directly obtained from the raw data
class TimeseriesDailyQ(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.FloatField(blank=True, null=True)
    class Meta:
        indexes = [
            models.Index(fields=['station', 'date'], name='q_station_day_idx')
        ]
        unique_together = ('station', 'date')

# The data is directly obtained from the raw data
class TimeseriesDailyWaterlevel(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date = models.DateField()
    level = models.FloatField(blank=True, null=True)
    class Meta:
        indexes = [
            models.Index(fields=['station', 'date'], name='station_day_idx')
        ]
        unique_together = ('station', 'date')

class TimeseriesMonthlyWaterlevel(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    month = models.DateField()
    level = models.FloatField(blank=True, null=True)

    # @property
    # def year(self):
    #     return self.month.year

    # @property
    # def month(self):
    #     return self.month.month
    # class Meta:
    #     indexes = [
    #         models.Index(fields=['station', 'month'], name='station_month_idx')
    #     ]
    #     unique_together = ('station', 'month')

class TimeseriesYearlyWaterlevel(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(null=True, blank=True)
    level = models.FloatField(blank=True, null=True)
    class Meta:
        indexes = [
            models.Index(fields=['station', 'year'], name='station_year_idx')
        ]
        unique_together = ('station', 'year')

# TODO this has probably uniquely only the TUB Data. The other data should also be in the other timeseries tables
class TimeseriesValues(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date = models.DateField()
    rainfall = models.FloatField(null=True, blank=True)
    waterlevel_above_sensor_cm = models.FloatField(null=True, blank=True)
    absolute_water_level_elevation_m = models.FloatField(null=True, blank=True)

# only used for forms
class MarWeighting(models.Model):
    aquifer_thickness = models.IntegerField(default=5)
    depth_groundwater = models.IntegerField(default=5)
    hydraulic_conductivity = models.IntegerField(default=5)
    land_use = models.IntegerField(default=5)
    distance_to_source_water = models.IntegerField(default=5)
    distance_to_well = models.IntegerField(default=5)

# search area for TU MAR
class LowerSpreeCachment(models.Model):
    geom25833 = gis_models.GeometryField(srid=25833)
    geom4326 = gis_models.GeometryField(srid=4326)
    area = models.FloatField()
    perimeter = models.FloatField()

class MarSliderDescription(models.Model):
    name_de = models.CharField(max_length=32, null=True, blank=True)
    name_en = models.CharField(max_length=32, null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

class MarSuitabilitySliderDescription(models.Model):
    name_de = models.CharField(max_length=32, null=True, blank=True)
    name_en = models.CharField(max_length=32, null=True, blank=True)
    suitability = models.IntegerField(null=True, blank=True)

##################

class MapLabels(models.Model):
    suitability = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(max_length=64)
    label_de = models.CharField(max_length=64, null=True, blank=True)
    label_en = models.CharField(max_length=64, null=True, blank=True)
    map_name = models.CharField(max_length=64)
    map_value = models.IntegerField(null=True)
    default_score = models.IntegerField()
    order_position = models.IntegerField()

class MarForbiddenArea(models.Model):
    geom25833 = gis_models.MultiPolygonField(srid=25833)

    
    

    ##########################




