import random
from django.db import models
from django.db.models import Min, Max, Q
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from buek.models import CorineLandCover2018
from django.contrib.gis.db.models.functions import Transform
from django.core.validators import MinValueValidator, MaxValueValidator
from toolbox import utils
import json
from datetime import datetime
class ToolboxType(models.Model):
    name_de = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    name_tag = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=255)

    def __str__(self, language='de'):
        return self.name_de if language == 'de' else self.name_en
    

# gw_ezg
# TODO: not used - delete or geoserver
class BelowGroundCatchmentArea(models.Model):
    uezg_id = models.CharField(max_length=100)
    haupt_ezg = models.CharField(max_length=100, null=True)
    teil_ezg = models.CharField(max_length=100,null=True)
    qru_m3_s = models.FloatField(null=True)
    flaeche_m2 = models.FloatField(null=True)
    bg_id = models.FloatField(null=True)
    geom25833 = gis_models.MultiPolygonField(srid=25833)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True)
 

    def __str__(self):
        return self.uezg_id
    
    def to_json(self, language='de'):
        return {
            'id': self.id,
            'uezg_id': self.uezg_id,
            'name': self.hapt_ezg,
            'qru_m3_s': self.qru_m3_s,
            'area_ha': round(self.flaeche_m2/10000, 1),
            'bg_id': self.bg_id,
            'haupt_ezg': self.haupt_ezg

            }
    
    def to_feature(self, epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

# ezg25 
# TODO: not used - delete or geoserver
class AboveGroundCatchmentArea(models.Model):
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
    geom25833 = gis_models.MultiPolygonField(srid=25833)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True)

    def __str__(self):
        return self.kennzahl

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Oberirdisches_Einzugsgebiet"
        elif language == 'en':
            return "Above_Ground_Catchment_Area"
    
    def to_json(self):
        return {
            "id": self.id,
            "name": 'Oberirdisches Einzugsgebiet',
            "kennzahl": self.kennzahl,
            "gewaesser": self.gewaesser,
            "gew_alias": self.gew_alias,
            "gew_kennz": self.gew_kennz,
            "beschr_von": self.beschr_von,
            "beschr_bis": self.beschr_bis,
            "land": self.land,
            "ordnung": self.ordnung,
            "fl_art": self.fl_art,
            "wrrl_kr": self.wrrl_kr,
            "area_qkm": round(self.area_qkm, 2),
            "area_ha": round(self.area_ha, 2),
            "ezg_id": self.ezg_id,
            "bemerkung": self.bemerkung,
            "wrrl_fge": self.wrrl_fge,
            "wrrl_bg": self.wrrl_bg,
            "color_index": (self.id % 50) * 5,  # different fill color for each catchment area
        }
    
    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            "kennzahl": {'field_type': "C", 'decimal': 0},
            "gewaesser": {'field_type': "C", 'decimal': 0},
            "gew_alias": {'field_type': "C", 'decimal': 0},
            "gew_kennz": {'field_type': "C", 'decimal': 0},
            "beschr_von": {'field_type': "C", 'decimal': 0},
            "beschr_bis": {'field_type': "C", 'decimal': 0},
            "land": {'field_type': "C", 'decimal': 0},
            "ordnung": {'field_type': "C", 'decimal': 0},
            "fl_art": {'field_type': "C", 'decimal': 0},
            "wrrl_kr": {'field_type': "C", 'decimal': 0},
            "area_qkm": {'field_type': "N", 'decimal': 0},
            "area_ha": {'field_type': "N", 'decimal': 0},
            "ezg_id": {'field_type': "N", 'decimal': 0},
            "bemerkung": {'field_type': "C", 'decimal': 0},
            "wrrl_fge": {'field_type': "C", 'decimal': 0},
            "wrrl_bg": {'field_type': "C", 'decimal': 0},

        }

    def to_feature(self, epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
    

    
class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_userfields")
    name = models.CharField(max_length=255)
    creation_date = models.DateField(blank=True, default=now)
    geom = gis_models.GeometryField(null=True, srid=4326)
    geom25833 = gis_models.GeometryField(null=True, srid=25833)
    has_infiltration = models.BooleanField(default=False, null=True, blank=True)
    has_injection = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_sink = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_gek = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_surface_water = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_wetland = models.BooleanField(default=False, null=True, blank=True)
    has_sieker_drainage = models.BooleanField(default=False, null=True, blank=True)
    toolbox_types = models.ManyToManyField(
        "ToolboxType",
        blank=True,
        related_name="user_fields"
    )
    filter_bounds = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Suchgebiet"
    
        elif language == 'en':
            return "Search_Area"

    def to_json(self):
        return {
                'id': self.id,
                'name': self.name,
                'user': self.user.id,
                'projects': [project for project in self.toolbox_projects.all().values('id', 'name', 'creation_date', 'last_modified')],
                'has_infiltration': self.has_infiltration,
                'has_injection': self.has_injection,
                'has_sieker_sink': self.has_sieker_sink,
                'has_sieker_gek': self.has_sieker_gek,
                'has_sieker_surface_water': self.has_sieker_surface_water,
                'has_sieker_wetland': self.has_sieker_wetland,
                'has_sieker_drainage': self.has_sieker_drainage,
        }
    
    @classmethod
    def shp_writer_fields(cls):
        return {
            'name': {'field_type': "C", 'decimal': 0},
        }
    
    def to_feature(self, epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

    def compute_filter_bounds_infiltration(self):
        bounds = dict()
        lakes = Lake.objects.filter(Q(geom__intersects=self.geom) | Q(geom__within=self.geom))
        streams = Stream.objects.filter(Q(geom__intersects=self.geom) | Q(geom__within=self.geom))
        sinks = Sink.objects.filter(centroid__within=self.geom)
        enlarged_sinks = EnlargedSink.objects.filter(centroid__within=self.geom)

        bounds['sinks'] = {
            'area': utils.get_bounds(sinks, 'area'),
            'depth': utils.get_bounds(sinks, 'depth'),
            'volume': utils.get_bounds(sinks, 'volume'),
        }

        bounds['enlarged_sinks'] = {
            'area': utils.get_bounds(enlarged_sinks, 'area'),
            'depth': utils.get_bounds(enlarged_sinks, 'depth'),
            'volume': utils.get_bounds(enlarged_sinks, 'volume'),
            'volume_construction_barrier': utils.get_bounds(enlarged_sinks, 'volume_construction_barrier'),
            'volume_gained': utils.get_bounds(enlarged_sinks, 'volume_gained'),
        }

        bounds['streams'] = {
            'min_surplus_volume': utils.get_bounds(streams, 'min_surplus_volume'),
            'mean_surplus_volume': utils.get_bounds(streams, 'mean_surplus_volume'),
            'max_surplus_volume': utils.get_bounds(streams, 'max_surplus_volume'),
            'plus_days': utils.get_bounds(streams, 'plus_days'),
        }

        bounds['lakes'] = {
            'min_surplus_volume': utils.get_bounds(lakes, 'min_surplus_volume'),
            'mean_surplus_volume': utils.get_bounds(lakes, 'mean_surplus_volume'),
            'max_surplus_volume': utils.get_bounds(lakes, 'max_surplus_volume'),
            'plus_days': utils.get_bounds(lakes, 'plus_days'),
        }

        # and similarly for streams/sinks/enlarged_sinks
        self.filter_bounds.update(bounds)
        self.save(update_fields=['filter_bounds'])
    
    def save(self, *args, **kwargs):
        if self.geom:
            self.geom25833 = self.geom.transform(25833, clone=True)

        # clear old relations
        super().save(*args, **kwargs)
        self.toolbox_types.clear()

        def add_toolbox(tag):
            tb = ToolboxType.objects.filter(name_tag=tag).first()
            if tb:
                self.toolbox_types.add(tb)

        # spatial checks
        if Sink.objects.filter(geom4326__intersects=self.geom).exists() \
        or EnlargedSink.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_infiltration = True
            add_toolbox("infiltration")

        if OutlineInjection.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_injection = True
            add_toolbox("injection")

        if SiekerSink.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_sieker_sink = True
            add_toolbox("sieker_sink")

        if GekRetention.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_sieker_gek = True
            add_toolbox("sieker_gek")

        if SiekerLargeLake.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_sieker_surface_water = True
            add_toolbox("sieker_surface_water")

        if HistoricalWetlands.objects.filter(geom4326__intersects=self.geom).exists():
            self.has_sieker_wetland = True
            add_toolbox("sieker_wetland")

        super().save(update_fields=[
            "has_infiltration",
            "has_injection",
            "has_sieker_sink",
            "has_sieker_gek",
            "has_sieker_surface_water",
            "has_sieker_wetland",
        ])



class ToolboxProject(models.Model):    
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_projects")
    description = models.TextField(null=True, blank=True)
    user_field = models.ForeignKey('UserField', on_delete=models.CASCADE, null=True, related_name="toolbox_projects")
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

    def to_feature(self, epsg=4326):
        """
        Convert the model instance to a GeoJSON feature.
        """
        if epsg == 4326:
            geometry = json.loads(self.geom.geojson) if self.geom else None
        else:
            raise ValueError("Unsupported EPSG code")
        
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

    
    def to_feature(self, epsg=4326):
        """
        Convert the model instance to a GeoJSON feature.
        """
        if epsg == 4326:
            geometry = json.loads(self.geom.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
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

# DE: Injektion/ Qgis _injektion_diss_4326
class OutlineInjection(gis_models.Model):
    """
    Area where injection projects can be evaluated
    """
    name = models.CharField(max_length=64, null=True, blank=True)
    geom25833 = gis_models.MultiPolygonField('Injection', srid=25833, null=True, blank=True)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
                return self.name
    
    
    def to_feature(self, epsg=4326):
        geometry = json.loads(self.geom.geojson)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {'name': self.name}
        }

class OutlineDrainage(gis_models.Model):
    """
    Area where injection projects can be evaluated
    """
    name = models.CharField(max_length=64, null=True, blank=True)
    geom25833 = gis_models.MultiPolygonField('Injection', srid=25833, null=True, blank=True)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
                return self.name
    
    
    def to_feature(self, epsg=4326):
        geometry = json.loads(self.geom.geojson)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {'name': self.name}
        }


# DE: Ufernah /Qgis: ufernah_diss_4326
class OutlineSurfaceWater(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Surface Water')

    def __str__(self):
            return self.name

    def to_feature(self, epsg=4326):
        geometry = json.loads(self.geom.geojson)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {'name': self.name}
        }

# DE: Versickerung / Qgis: versickerung_diss_4326
class OutlineInfiltration(gis_models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.MultiPolygonField('Infiltration')  

    def __str__(self):
            return self.name

    def to_feature(self, epsg=4326):
        geometry = json.loads(self.geom.geojson)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {'name': self.name}
        }

    

### ---- 2024-12-02 ---- ###

#Quoek_qn_9115
class Quoek(models.Model):
    id = models.IntegerField(primary_key=True)  # THIS IS FGW_ID
    geom25833 = gis_models.MultiLineStringField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.MultiLineStringField(srid=4326, null=True, blank=True)
    gewaesser = models.CharField(max_length=100, null=True, blank=True)
    gewaesser_gn2 = models.CharField(max_length=100, null=True, blank=True) 
    
    ezg25_km2 = models.FloatField(null=True, blank=True)
    mq_qn = models.FloatField(null=True, blank=True)
    mnq_qn = models.FloatField(null=True, blank=True)
    wkid_2021 = models.IntegerField(null=True, blank=True)
    kat_2021 = models.CharField(max_length=100, null=True, blank=True)
    typ_2021 = models.CharField(max_length=100, null=True, blank=True)
    mow_2021 = models.FloatField(null=True, blank=True)
    q_oek = models.FloatField(null=True, blank=True)
    laenge_km = models.FloatField(null=True, blank=True)
    fgw_unterlauf_id = models.IntegerField(null=True, blank=True)

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
    # fgw_id = models.IntegerField(null=True, blank=True)
    fgw = models.ForeignKey(Quoek, on_delete=models.CASCADE, null=True, blank=True)  # ArcEGMO-ID des Fließgewässerabschnittes
    # Ökologisch begründete Mindestwasserführung hergeleitet für den 3. BWZ ab 2021 (EZG x MOW / 1000)
    minimum_environmental_flow = models.FloatField(null=True, blank=True) # - m³/s  -777 kein berichtspflichtiger OWK; -999 künstlicher OWK
    q_mean = models.FloatField(null=True, blank=True) # m³/s - mittlerer Abfluss des Fließgewässers (Quoek) - wird für die Berechnung der Umweltwasserführung herangezogen
    shape_length = models.FloatField()
    # id_source = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()
    geom = gis_models.LineStringField(srid=4326, null=True, blank=True)
    geom25833 = gis_models.MultiLineStringField(srid=25833, null=True, blank=True)

    def __data_type__(self):
        return 'stream'

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Fliessgewaesser"
        elif language == 'en':
            return "Streams"

    def to_json(self, language='de'):
        return {
                'id': self.id,
                'name': self.name,
                'fgw_id': self.fgw.id if self.fgw else None,
                'shape_length': round(self.shape_length),
                'minimum_environmental_flow': self.minimum_environmental_flow,
                'q_mean': self.q_mean,
                'min_surplus_volume': round(self.min_surplus_volume),
                'mean_surplus_volume': round(self.mean_surplus_volume),
                'max_surplus_volume': round(self.max_surplus_volume),
                'plus_days': self.plus_days
        }
    
    @classmethod
    def shp_writer_fields(cls):
        return {
                'id': {'field_type': "N", 'decimal': 0},
                'name': {'field_type': "C", 'decimal': 0},
                'fgw_id': {'field_type': "N", 'decimal': 0},
                'shape_length': {'field_type': "N", 'decimal': 0},
                'minimum_environmental_flow': {'field_type': "F", 'decimal': 2},
                'min_surplus_volume': {'field_type': "F", 'decimal': 4},
                'mean_surplus_volume': {'field_type': "F", 'decimal': 0},
                'max_surplus_volume': {'field_type': "F", 'decimal': 0},
                'plus_days': {'field_type': "F", 'decimal': 0},
        }
    
    def to_feature(self, language='de', epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json(language=language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
    
class Lake(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    # fgw_id = models.IntegerField(null=True, blank=True)  
    fgw = models.ForeignKey(Quoek, on_delete=models.CASCADE, null=True, blank=True)  # ArcEGMO-ID des Fließgewässerabschnittes
    # Ökologisch begründete Mindestwasserführung hergeleitet für den 3. BWZ ab 2021 (EZG x MOW / 1000)
    minimum_environmental_flow = models.FloatField(null=True, blank=True) # - m³/s  -777 kein berichtspflichtiger OWK; -999 künstlicher OWK
    q_mean = models.FloatField(null=True, blank=True) # m³/s - mittlerer Abfluss des zugeordneten Fließgewässers (Quoek) - wird für die Berechnung der Umweltwasserführung herangezogen
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

    def __data_type__(self):
        return 'lake'
    
    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Seen"
        elif language == 'en':
            return "Lakes"

    def to_json(self, language='de'):
        return {
                'id': self.id,
                'name': self.name,
                'fgw_id': self.fgw.id if self.fgw else None,
                # 'shape_length': round(self.shape_length, 2),
                'shape_area': round(self.shape_area),
                'minimum_environmental_flow': self.minimum_environmental_flow,
                'q_mean': self.q_mean,
                'min_surplus_volume': round(self.min_surplus_volume),
                'mean_surplus_volume': round(self.mean_surplus_volume),
                'max_surplus_volume': round(self.max_surplus_volume),
                'plus_days': self.plus_days
        }
    
    @classmethod
    def shp_writer_fields(cls):
        return {
                'id': {'field_type': "N", 'decimal': 0},
                'name': {'field_type': "C", 'decimal': 0},
                'fgw_id': {'field_type': "N", 'decimal': 0},
                # 'shape_length': {'field_type': "N", 'decimal': 0},
                'shape_area': {'field_type': "N", 'decimal': 0},
                'minimum_environmental_flow': {'field_type': "F", 'decimal': 2},
                'min_surplus_volume': {'field_type': "F", 'decimal': 4},
                'mean_surplus_volume': {'field_type': "F", 'decimal': 0},
                'max_surplus_volume': {'field_type': "F", 'decimal': 0},
                'plus_days': {'field_type': "F", 'decimal': 0},
        }
    
    def to_feature(self, language='de', epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json(language=language)
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

    def __data_type__(self):
        return "sink"

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Senken"
        elif language == 'en':
            return "Sinks"
   
    def to_json(self, indices, language='de'):
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
            "name": 'Senke' if language=='de' else 'Sink',
            "depth": round(self.depth, 2),
            "area": round(self.area),
            "volume": round(self.volume),
            "index_proportions": round(self.index_proportions * 100),
            "index_soil": round(indices[self.id]['index_soil'] * 100),
            "landuse": landuse,
            "landuse_1": landuse_1,
            'landuse_1_percentage': round(self.land_use_1_percentage or 0, 1),
            "landuse_2": landuse_2,
            'landuse_2_percentage': round(self.land_use_2_percentage or 0, 1),
            "landuse_3": landuse_3,
            'landuse_3_percentage': round(self.land_use_3_percentage or 0, 1),
            "soil_points": self.soil_points,
            "index_feasibility": int(self.index_feasibility * 100) if self.index_feasibility else "-",
            "hydrogeology": getattr(self.aquifer, f'name_{language}', None),
            "index_hydrogeology": int(self.index_hydrogeology * 100) if self.index_hydrogeology else None,
            "index_sink_total": min(int(indices[self.id]['index_sink_total'] * 100), 100),
        }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'depth': {'field_type': "F", 'decimal': 2},
            'area': {'field_type': "N", 'decimal': 0},
            'volume': {'field_type': "N", 'decimal': 0},
            'index_proportions': {'field_type': "F", 'decimal': 2},
            'index_soil': {'field_type': "F", 'decimal': 2},
            'landuse_1': {'field_type': "C", 'decimal': 0},
            'landuse_1_percentage': {'field_type': "F", 'decimal': 1},
            'landuse_2': {'field_type': "C", 'decimal': 0},
            'landuse_2_percentage': {'field_type': "F", 'decimal': 1},
            'landuse_3': {'field_type': "C", 'decimal': 0},
            'landuse_3_percentage': {'field_type': "F", 'decimal': 1},
            'soil_points': {'field_type': "C", 'decimal': 0},
            'index_feasibility': {'field_type': "F", 'decimal': 2},
            'hydrogeology_text': {'field_type': "C", 'decimal': 0},
            'index_hydrogeology': {'field_type': "F", 'decimal': 2},
            'index_sink_total': {'field_type': "F", 'decimal': 0},
        }

    def to_point_feature(self, indices, epsg=4326, language='de'):  
        if epsg == 25833:
            geometry = json.loads(self.geom25833.centroid.geojson)    
        else:
            geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(indices, language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

    def to_feature(self, indices, epsg=4326, language='de'):      
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        properties = self.to_json(indices, language)
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
    construction_plat_width = models.FloatField(null=True)
    construction_height = models.FloatField(null=True)
    construction_geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    construction_geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
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

    def __data_type__(self):
        return "enlarged_sink"

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Vergroesserte_Senken"
        elif language == 'en':
            return "Enlarged_Sinks"

    def to_json(self, indices, language='de'):

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
            "name": 'Vergrößerte Senke' if language=='de' else 'Enlarged Sink',
            "depth": round(self.depth, 2),
            "area": round(self.area),
            "volume": round(self.volume),
            "index_proportions": int(self.index_proportions * 100),
            "index_soil": round(indices[self.id]['index_soil'] * 100),
            "landuse": landuse,
            "landuse_1": landuse_1,
            "landuse_1_percentage": round(self.land_use_1_percentage or 0, 1),
            "landuse_2": landuse_2,
            "landuse_2_percentage": round(self.land_use_2_percentage or 0, 1),
            "landuse_3": landuse_3,
            "landuse_3_percentage": round(self.land_use_3_percentage or 0, 1),
            "landuse_4": landuse_4,
            "landuse_4_percentage": round(self.land_use_4_percentage or 0, 1),
            "volume_gained": round(self.volume_gained) if self.volume_gained else None,
            "volume_construction_barrier": round(self.volume_construction_barrier) if self.volume_construction_barrier else None,     
            "soil_points": self.soil_points,
            "index_feasibility": int(self.index_feasibility * 100) if self.index_feasibility else "-",
            "hydrogeology": getattr(self.aquifer, f'name_{language}', None),
            "index_hydrogeology": int(self.index_hydrogeology * 100) if self.index_hydrogeology else None,
            "index_sink_total": min(int(indices[self.id]['index_sink_total'] * 100), 100),
        }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'depth': {'field_type': "F", 'decimal': 2},
            'area': {'field_type': "N", 'decimal': 0},
            'volume': {'field_type': "N", 'decimal': 0},
            'index_proportions': {'field_type': "F", 'decimal': 2},
            'index_soil': {'field_type': "F", 'decimal': 2},
            'landuse_1': {'field_type': "C", 'decimal': 0},
            'landuse_1_percentage': {'field_type': "F", 'decimal': 1},
            'landuse_2': {'field_type': "C", 'decimal': 0},
            'landuse_2_percentage': {'field_type': "F", 'decimal': 1},
            'landuse_3': {'field_type': "C", 'decimal': 0},
            'landuse_3_percentage': {'field_type': "F", 'decimal': 1},
            'landuse_4': {'field_type': "C", 'decimal': 0},
            'landuse_4_percentage': {'field_type': "F", 'decimal': 1},
            'volume_construction_barrier': {'field_type': "N", 'decimal': 0},
            'volume_gained': {'field_type': "N", 'decimal': 0},
            'soil_points': {'field_type': "C", 'decimal': 0},
            'index_feasibility': {'field_type': "F", 'decimal': 2},
            'hydrogeology_text': {'field_type': "C", 'decimal': 0},
            'index_hydrogeology': {'field_type': "F", 'decimal': 2},
            'index_sink_total': {'field_type': "N", 'decimal': 0},
        }
       
    
    def to_point_feature(self, indices, epsg=4326, language='de'):  
        if epsg == 25833:
            geometry = json.loads(self.geom25833.centroid.geojson)    
        else:
            geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(indices, language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

    def to_feature(self, indices, epsg=4326, language='de'):      
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")

        properties = self.to_json(indices, language)
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
    geom25833 = gis_models.MultiPolygonField(srid=25833)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='sink_embankment') 

    fid_sink = models.IntegerField()
    height = models.FloatField()
    plat_width = models.FloatField()
    volume = models.FloatField()

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)


    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Verwallungen"
        elif language == 'en':
            return "Embankments"

    def to_feature(self, epsg=4326, language='de'):
        """
        Convert the model instance to a GeoJSON feature.
        """
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": self.id,
                "name": 'Verwallung' if language=='de' else 'Embankment',
                "enlargedSinkId": self.enlarged_sink.id if self.enlarged_sink else None,
                "height": self.height,
                "plat_width": self.plat_width,
                "volume": self.volume,
            }
        }
    
    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            # 'enlargedSinkId': {'field_type': "N", 'decimal': 0},
            'height': {'field_type': "F", 'decimal': 2},
            'plat_width': {'field_type': "F", 'decimal': 2},
            'volume': {'field_type': "N", 'decimal': 0},
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
    soil_properties = models.ForeignKey(SoilProperties, on_delete=models.DO_NOTHING, blank=True, null=True, )
    sink = models.ForeignKey(Sink, on_delete=models.DO_NOTHING, null=True, related_name='sink_soil_properties')   
    sink_fid = models.IntegerField(null=True, blank=True)  # former fid_sink
# Intersection of SoilProperties and EnlargedSink
class EnlargedSinkSoilProperties(models.Model):
    geom = gis_models.GeometryField(srid=4326, blank=True, null=True)
    partial_sink_area = models.FloatField(blank=True, null=True)
    percent_of_total_area = models.FloatField(blank=True, null=True)
    soil_properties = models.ForeignKey(SoilProperties, on_delete=models.DO_NOTHING, blank=True, null=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING,  blank=True, null=True, related_name='enlarged_sink_soil_properties')

# Quoek 




class DischargeTimeseries(models.Model):
    stream = models.ForeignKey(Stream,  on_delete=models.CASCADE, related_name='discharge_timeseries_stream', null=True, blank=True) 
    lake = models.ForeignKey(Lake,  on_delete=models.CASCADE, related_name='discharge_timeseries_lake', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    discharge_m3s = models.FloatField(null=True, blank=True)
    fgw = models.ForeignKey(Quoek, on_delete=models.CASCADE, null=True, blank=True)

class SiekerLargeLake(models.Model):
    geom25833 = gis_models.PolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    stand = models.DateField(null=True, blank=True) ##
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
    trend_cm_per_a = models.FloatField(null=True, blank=True) # trend in cm /jahr
    seetyp = models.IntegerField(null=True, blank=True)
    seetyp_txt = models.CharField(max_length=100, null=True, blank=True)

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Grosse_Seen"
        elif language == 'en':
            return "Large_Lakes"

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
                "number_of_swimming_spots": self.number_of_swimming_spots,
                "quelldat": self.quelldat.isoformat() if self.quelldat else None,
                "area_m2": round(self.area_m2) if self.area_m2 else None,
                "area_ha": round(self.area_ha, 1) if self.area_ha else None,
                "vol_mio_m3": round(self.vol_mio_m3) if self.vol_mio_m3 else None,
                "einzugsgebiet_km2": self.einzugsgebiet_km2,
                "d_max_m": self.d_max_m,
                "verweilt": self.verweilt,
                "trend_cm_per_a": round(self.trend_cm_per_a, 2) if self.trend_cm_per_a else self.trend_cm_per_a,
                "seetyp": self.seetyp,
                "seetyp_txt": self.seetyp_txt,
                "color_index": 195, # fixed fill color for lakes
            }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'stand': {'field_type': "C", 'decimal': 0},
            'wrrl_pg': {'field_type': "C", 'decimal': 0},
            'genese': {'field_type': "C", 'decimal': 0},
            'wrrl': {'field_type': "N", 'decimal': 0},
            'number_of_swimming_spots': {'field_type': "N", 'decimal': 0},
            'area_m2': {'field_type': "N", 'decimal': 0},
            'area_ha': {'field_type': "F", 'decimal': 1},
            'vol_mio_m3': {'field_type': "N", 'decimal': 0},
            'einzugsgebiet_km2': {'field_type': "F", 'decimal': 2},
            'd_max_m': {'field_type': "N", 'decimal': 0},
            'verweilt': {'field_type': "C", 'decimal': 0},
            'trend_cm_per_a': {'field_type': "F", 'decimal': 2},
            'seetyp': {'field_type': "N", 'decimal': 0},
            'seetyp_txt': {'field_type': "C", 'decimal': 0},
        }

    def to_feature(self, epsg=4326, language='de'):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

class PegelOnline(models.Model):
    uuid = models.CharField(max_length=52)
    number = models.BigIntegerField(null=True, blank=True)
    shortname = models.CharField(max_length=100, null=True, blank=True)
    longname = models.CharField(max_length=200, null=True, blank=True)
    km = models.FloatField(null=True, blank=True)
    agency = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    geom = gis_models.PointField(srid=4326, null=True, blank=True)
    water_shortname = models.CharField(max_length=100, null=True, blank=True)
    water_longname = models.CharField(max_length=200, null=True, blank=True)

# TU Station
class Station(models.Model):
    name = models.CharField(max_length=50)
    waterbody = models.CharField(max_length=64, null=True, blank=True)
    geom = gis_models.PointField(srid=25833, null=True, blank=True)
    data_provider = models.CharField(max_length=32)
    absolute_elevation_of_sensor_m = models.FloatField(null=True, blank=True)
    gauge_zero = models.FloatField(null=True, blank=True)
    station_number = models.IntegerField(null=True, blank=True)

class SiekerWaterLevel(models.Model):
    geom25833 = gis_models.PointField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.PointField(srid=4326, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)#
    station = models.ForeignKey(Station, on_delete=models.DO_NOTHING, null=True, blank=True)
    t_d = models.IntegerField(null=True, blank=True)  
    t_a = models.FloatField(null=True, blank=True)
    # startdatum = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    # enddatum = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    min_cm = models.IntegerField(null=True, blank=True)  
    max_cm = models.IntegerField(null=True, blank=True)  
    mw_10_19 = models.FloatField(null=True, blank=True)  # Mittelwert 2010-2019
    mw_90_99 = models.FloatField(null=True, blank=True)  # Mittelwert 1990 - 1999
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

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Wasserstand_Pegel"
        elif language == 'en':
            return "WaterLevel_Stations"
        

    def to_json(self, language='de'):
        if (language == 'de'):
            start_date = datetime.strftime(self.start_date, '%d.%m.%Y')
            end_date = datetime.strftime(self.end_date, '%d.%m.%Y')
        else:
            start_date = self.start_date.isoformat()
            end_date = self.end_date.isoformat()
        return {
            "id": self.id,
            "name": self.name,
            "t_d": self.t_d,
            "t_a": round(self.t_a),
            "period": f"{start_date} - {end_date}",
            "min_cm": self.min_cm,
            "max_cm": self.max_cm,
            "mw_10_19": int(self.mw_10_19) if self.mw_10_19 else self.mw_10_19,
            "mw_90_99": int(self.mw_90_99) if self.mw_90_99 else self.mw_90_99,
            "stdev_cm": self.stdev_cm,
            "twenty_yr_trend": round(self.twenty_yr_trend, 2) if self.twenty_yr_trend else self.twenty_yr_trend,
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
    
    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            't_d': {'field_type': "N", 'decimal': 0},
            't_a': {'field_type': "F", 'decimal': 2},
            'period': {'field_type': "C", 'decimal': 0},
            'min_cm': {'field_type': "N", 'decimal': 0},
            'max_cm': {'field_type': "N", 'decimal': 0},
            'mw_10_19': {'field_type': "N", 'decimal': 0},
            'mw_90_99': {'field_type': "N", 'decimal': 0},
            'stdev_cm': {'field_type': "F", 'decimal': 2},
            'twenty_yr_trend': {'field_type': "F", 'decimal': 2},
            'pkz': {'field_type': "C", 'decimal': 0},
            'pegelname': {'field_type': "C", 'decimal': 0},
            'gewaesser': {'field_type': "C", 'decimal': 0},
            'pegelart': {'field_type': "C", 'decimal': 0},
            'mess_w': {'field_type': "C", 'decimal': 0},
            'mess_q': {'field_type': "C", 'decimal': 0},
            'soll_w': {'field_type': "C", 'decimal': 0},
            'soll_q': {'field_type': "C", 'decimal': 0},
            'region': {'field_type': "C", 'decimal': 0},
            'hwmp': {'field_type': "N", 'decimal': 0},
            'dgjp': {'field_type': "N", 'decimal': 0},
            'gwk': {'field_type': "C", 'decimal': 0},
            'gbk': {'field_type': "C", 'decimal': 0},
            'a_ezg': {'field_type': "F", 'decimal': 2},
            'bemerkung': {'field_type': "C", 'decimal': 0},
            'anfrage': {'field_type': "C", 'decimal': 0},
            'stat': {'field_type': "C", 'decimal': 0},
            'ent_quell': {'field_type': "N", 'decimal': 0},
            'ent_muend': {'field_type': "N", 'decimal': 0},
            'diff_cm': {'field_type': "N", 'decimal': 0},
        }

    def to_feature(self, epsg=4326, language='de'):
        
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        

        properties = self.to_json(language)
        return {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }



class SiekerSink(models.Model):
    geom25833 = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    geom4326 = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
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
    distance_t = models.FloatField(null=True, blank=True) # distance to stream
    dist_lake = models.CharField(max_length=100, null=True, blank=True)
    umsetzbark = models.CharField(max_length=100, null=True, blank=True)
    index_feasibility = models.FloatField(null=True, blank=True)
    waterdist = models.CharField(max_length=100, null=True, blank=True)
    distance_lake = models.FloatField(null=True, blank=True)
    nearest_lake = models.ForeignKey(Lake, on_delete=models.DO_NOTHING, null=True, blank=True)
    distance_stream = models.FloatField(null=True, blank=True)
    nearest_stream = models.ForeignKey(Stream, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    def __data_type__(self):
        return "sink"

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Senken"
        elif language == 'en':
            return "Sinks"

    def to_json(self, language='de'):
        return {
                "id": self.id,
                "name": 'Senke' if language=='de' else 'Sink',
                "depth": round(self.depth, 2),
                "area": round(self.area),
                "volume": round(self.volume),
                "avg_depth": round(self.avg_depth, 2),
                "max_elevation": round(self.max_elevation, 1),
                "min_elevation": round(self.min_elevation, 1),
                "urbanarea_percent": self.urbanarea_percent,
                "wetlands_percent": self.wetlands_percent,
                "distance_t": int(self.distance_t),
                "dist_lake": self.dist_lake,
                "waterdist": self.waterdist,
                "umsetzbark": self.umsetzbark,
                "index_feasibility": int(self.index_feasibility * 100),
                "distance_lake": int(self.distance_lake),
                "nearest_lake": self.nearest_lake.name,
                "distance_stream": int(self.distance_stream),
                "nearest_stream": self.nearest_stream.name,
               
            }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'depth': {'field_type': "F", 'decimal': 2},
            'area': {'field_type': "N", 'decimal': 0},
            'volume': {'field_type': "N", 'decimal': 0},
            'avg_depth': {'field_type': "F", 'decimal': 2},
            'max_elevation': {'field_type': "F", 'decimal': 1},
            'min_elevation': {'field_type': "F", 'decimal': 1},
            'urbanarea_percent': {'field_type': "F", 'decimal': 2},
            'wetlands_percent': {'field_type': "F", 'decimal': 2},
            'distance_t': {'field_type': "N", 'decimal': 0},
            'dist_lake': {'field_type': "C", 'decimal': 0},
            'waterdist': {'field_type': "C", 'decimal': 0},
            'umsetzbark': {'field_type': "C", 'decimal': 0},
            'index_feasibility': {'field_type': "N", 'decimal': 0},
            'distance_lake': {'field_type': "N", 'decimal': 0},
            'nearest_lake': {'field_type': "C", 'decimal': 0},
            'distance_stream': {'field_type': "N", 'decimal': 0},
            'nearest_stream': {'field_type': "C", 'decimal': 0},
        }

    def to_point_feature(self, epsg=4326, language='de'):      
        if epsg == 25833:
            geometry = json.loads(self.geom25833.centroid.geojson)
        else:
            geometry = json.loads(self.centroid.geojson)
        properties = self.to_json(language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    
    def to_feature(self, epsg=4326, language='de'):  
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
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

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Wasserrueckhalteraeume"
        elif language == 'en':
            return "Water_Retention_Areas"

    def to_json(self, language='de'):
        landuses = self.landuses.all().order_by('-area_percentage')
        landuses_list = [f'{lu.clc_landuse.label_level_3_de} {round(lu.area_percentage *100)}%' for lu in landuses]
        landuses_str = ', \n'.join(landuses_list)
        
        return {
            "id": self.id,
            "name": self.name,
            "quelle_1": self.quelle_1,
            "quelle_2": self.quelle_2,
            "current_landusage": landuses_str,
            "association": self.association,
            "planning_segment": self.planning_segment,
            "hrsg": self.hrsg,
            "document": self.gek_document.link,
            "number_of_measures": self.number_of_measures,
        }
    
    

    def to_feature(self, epsg=4326, language='de'):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json()
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
    
    @ classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'quelle_1': {'field_type': "C", 'decimal': 0},
            'quelle_2': {'field_type': "C", 'decimal': 0},
            'current_landusage': {'field_type': "C", 'decimal': 0},
            'association': {'field_type': "C", 'decimal': 0},
            'planning_segment': {'field_type': "C", 'decimal': 0},
            'hrsg': {'field_type': "C", 'decimal': 0},
            'document': {'field_type': "C", 'decimal': 0},
            'number_of_measures': {'field_type': "N", 'decimal': 0},
        }


# m:n table 
class GekLanduse(models.Model):
    gek_retention = models.ForeignKey(GekRetention, on_delete=models.CASCADE, related_name='landuses')
    current_landuse = models.CharField(max_length=100, null=True, blank=True) # derz_nutzu Original Data!
    first_two_clc_digits = models.CharField(max_length=3, null=True, blank=True) # CLC code
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
    priority_value = models.FloatField(null=True, blank=True) 
    kosten = models.CharField(max_length=100, null=True, blank=True)
    costs_2013 = models.IntegerField(null=True, blank=True)  # Kosten in Euro
    costs = models.IntegerField(null=True, blank=True) # Adjusted for 2025 1st Quarter
    measure_number = models.IntegerField(null=True, blank=True)  # Maßnahme Nummer (2 in 2MNT_ID)
    specific_document = models.CharField(max_length=255, null=True, blank=True)
    kosten_aktuell = models.CharField(max_length=100, null=True, blank=True)

    
    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Massnahmen_Wasserruekhalteraeume"
        elif language == 'en':
            return "Measures_Water_Retention_Areas"


    def to_json(self, language='de'):
        return {
            "id": self.id,
            "gek_measure": self.gek_measure.description_de if language == 'de' else self.gek_measure.description_en,
            "quantity": self.quantity,
            "description": getattr(self, f'description_{language}', None),
            "priority": self.priority.description_de if language == 'de' else self.priority.description_en,
            "priority_value": self.priority_value,
            # "kosten": self.kosten,
            "costs": self.costs,
            "measure_number": self.measure_number
            }

    # TODO: Implement SHP writer fields; for shp export it needs the geom and retention infos
    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'quelle_1': {'field_type': "C", 'decimal': 0},
            'quelle_2': {'field_type': "C", 'decimal': 0},
            'current_landusage': {'field_type': "C", 'decimal': 0},
            'association': {'field_type': "C", 'decimal': 0},
            'planning_segment': {'field_type': "C", 'decimal': 0},
            'hrsg': {'field_type': "C", 'decimal': 0},
            'document': {'field_type': "C", 'decimal': 0},
            'number_of_measures': {'field_type': "N", 'decimal': 0},
            'gek_measure': {'field_type': "C", 'decimal': 0},
            'quantity': {'field_type': "F", 'decimal': 2},
            'description': {'field_type': "C", 'decimal': 0},
            'priority': {'field_type': "C", 'decimal': 0},
            'priority_value': {'field_type': "F", 'decimal': 2},
            # 'kosten': {'field_type': "C", 'decimal': 0},
            'costs': {'field_type': "N", 'decimal': 0},
            'measure_number': {'field_type': "N", 'decimal': 0},
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

    def __data_type__(self):
        return 'wetland'


    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Historische_Feuchtgebiete"
        elif language == 'en':
            return "Historical_Wetlands"

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

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'comment': {'field_type': "C", 'decimal': 0},
            'current_landusage': {'field_type': "C", 'decimal': 0},
            'association': {'field_type': "C", 'decimal': 0},
            'source_1': {'field_type': "C", 'decimal': 0},
            'source_2': {'field_type': "C", 'decimal': 0},
            'source_3': {'field_type': "C", 'decimal': 0},
            'feasibility': {'field_type': "C", 'decimal': 0},
            'index_feasibility': {'field_type': "F", 'decimal': 2},
        }
    
    
    def to_feature(self, language='de', epsg=4326):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        properties = self.to_json(language=language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

def default_legend_labels():
    """
    This Dictionary sets the labels on a map legend. The number value is the one set in color_by_index.
    """
    return {'header': '', 'label_by_value': ''}

class LeafletLegend(models.Model):
    ramp = models.BooleanField(default=False)
    header_de = models.CharField(max_length=64)
    header_en = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.header_de

    def to_json(self, language='de'):
        grades = self.grades.all().order_by('order_position')
        legend = {
            'header': getattr(self, f'header_{language}'),
            'isRamp': self.ramp,
            'valsToColor': [g.value_to_color for g in self.grades.all().order_by('order_position')],
            'colors': [g.color for g in self.grades.all().order_by('order_position')],
            'gradientLabels': [getattr(g, f'label_{language}') for g in grades],
        }
        
        return legend
    

class LegendGrade(models.Model):
    leaflet_legend = models.ForeignKey(LeafletLegend, on_delete=models.CASCADE, related_name="grades")
    # ramp = models.BooleanField(default=False)
    color = models.CharField(max_length=10, null=True, blank=True)
    value_to_color = models.FloatField(null=True, blank=True)
    label_de = models.CharField(max_length=64)
    label_en = models.CharField(max_length=64, null=True, blank=True)
    order_position = models.PositiveIntegerField(default=0)

class DataInfo(models.Model):
    data_type = models.CharField(max_length=255)  # e.g. 'sieker_gek'
    feature_color = models.CharField(max_length=255, default="var(--bs-secondary)") # string defining the (bootstrap) color
    class_name = models.CharField(max_length=255)
    feature_type = models.CharField(max_length=255, default="polygon", null=True, blank=True)
    table_caption = models.CharField(max_length=255)
    popup_header = models.CharField(max_length=255, null=True, blank=True)  # e.g. "name"
    marker_cluster = models.BooleanField(default=False, null=True, blank=True) # TODO not used!
    color_by_index = models.CharField(default=None, max_length=32, null=True, blank=True)
    # a legend is only created if color_by_index is not None 
    legend = models.ForeignKey(LeafletLegend, on_delete=models.CASCADE, default=None, null=True, blank=True)
    # icon path is relevant for point values, that have a custom pin icon
    icon_path = models.CharField(max_length=256, null=True, blank=True)
    # style of a dashed line
    dash_array = models.CharField(max_length=8, null=True, blank=True)
    select_feature_button = models.BooleanField(default=False)

    def to_json(self, language="de"):
        dict = {
            "dataType": self.data_type,
            "featureColor": self.feature_color,
            "className": self.class_name,
            "featureType": self.feature_type,
            "tableCaption": self.table_caption,
            "popUp": {"header": self.popup_header},
            "properties": [p.to_json(language) for p in self.properties.all().order_by('order_position')],
            "tableLength": self.properties.filter(table=True).count(),
            "selectFeatureButton": self.select_feature_button,
            
        }
        if self.color_by_index:
            dict.update({"colorByIndex": self.color_by_index})
        if self.icon_path:
            dict.update({"pinIconPath": self.icon_path})
        if self.legend:
            dict.update({"legendSettings": self.legend.to_json(language)})
        if self.dash_array:
            dict.update({"dashArray": self.dash_array})

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
    help_text = models.CharField(max_length=512, null=True, blank=True)

    def to_json(self, language="de"):
        property = {
            "popUp": self.popup,
            "table": self.table,
            "title": getattr(self, f'title_{language}', None),
            "valueName": self.value_name,
            "unit": self.unit,
            "href": self.href,
        }
        if self.help_text:
            property.update({"helpText": self.help_text})
         
        return property
    


## TU Berlin


# TODO: what is this? amount m³/s. The data is directly obtained from the raw data
# TODO delete. It is the ids 168, 170, 172, 173, 176,177 that are also in toolbox_timeseriesdailywaterlevel
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


######## TU MAR ##################
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
    """
    Infos about base raster files used in TU Berlin Injection.
    """
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
class DrainedAreaType(models.Model):
    name_tag = models.CharField(max_length=64, null=True, blank=True)
    name_de = models.CharField(max_length=64)
    name_en = models.CharField( max_length=64, null=True, blank=True)
    eww = models.IntegerField(null=True, blank=True)

class DrainedArea(models.Model):
    geom25833 = gis_models.PolygonField(srid=25833)
    geom4326 = gis_models.PolygonField(srid=4326, null=True, blank=True)
    drained_area_type = models.ForeignKey(DrainedAreaType, on_delete=models.DO_NOTHING,  null=True, blank=True)

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Entwaesserte_Gebiete"
        elif language == 'en':
            return "Drained_Areas"

    def to_json(self, language='de'):
        return {
            'id': self.id,
            'drained_area_type_id': self.drained_area_type.id,
            'area': int(self.geom25833.area),
            'name': self.drained_area_type.name_de if language=='de' else self.drained_area_type.name_en,
            'drained_area_type': self.drained_area_type.name_tag,
        }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'drained_area_type_id': {'field_type': "N", 'decimal': 0},
            'area': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'drained_area_type': {'field_type': "C", 'decimal': 0},
        }
    
    def to_feature(self, epsg=4326, language='de'):
        if epsg == 4326:
            geometry = json.loads(self.geom4326.geojson)
        elif epsg == 25833:
            geometry = json.loads(self.geom25833.geojson)
        else:
            raise ValueError("Unsupported EPSG code")
        
        properties = self.to_json(language=language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
class DrainageNetworkType(models.Model):
    name_tag = models.CharField(max_length=100, null=True, blank=True)
    name_de = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)


class DrainageNetworkTypeDetail(models.Model):
    # name_de = models.CharField(max_length=100, null=True, blank=True)
    name_de = models.CharField(max_length=255, null=True, blank=True)
    name_tag = models.CharField(max_length=255, null=True, blank=True)
    network_type = models.ForeignKey(DrainageNetworkType, on_delete=models.CASCADE, related_name='details', null=True, blank=True)

class DrainageNetwork(models.Model):
    geom25833 = gis_models.LineStringField(srid=25833)
    geom4326 = gis_models.LineStringField(srid=4326, null=True, blank=True)
    total_length_m = models.FloatField(null=True, blank=True)
    network_type_detail = models.ForeignKey(DrainageNetworkTypeDetail, on_delete=models.DO_NOTHING, null=True, blank=True)

    @classmethod
    def get_filename(cls, language='de'):
        if language == 'de':
            return "Entwaesserungsnetz"
        return "drainage_network"


    def to_json(self, language='de'):
        return {
            'id': self.id,
            'name': self.network_type_detail.name_de if language== 'de' else self.network_type_detail.name_en,
            'length_m': int(self.geom25833.length),
            'network_type_id': self.network_type_detail.id,
            'network_type': self.network_type_detail.name_de if language=='de' else self.network_type_detail.name_en,
        }

    @classmethod
    def shp_writer_fields(cls):
        return {
            'id': {'field_type': "N", 'decimal': 0},
            'name': {'field_type': "C", 'decimal': 0},
            'length_m': {'field_type': "N", 'decimal': 0},
            'network_type_id': {'field_type': "N", 'decimal': 0},
            'network_type': {'field_type': "C", 'decimal': 0},
        }
    

    def to_feature(self, epsg=4326, language='de'):
        geometry = json.loads(self.geom4326.geojson)
        properties = self.to_json(language=language)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }


