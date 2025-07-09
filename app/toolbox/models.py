from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
from django.utils.timezone import now
from buek.models import CorineLandCover2018
from django.contrib.gis.db.models.functions import Transform
import json
class ToolboxType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    



# class DigitalElevationModel10(models.Model):
#      name = models.CharField(max_length=100, null=True, blank=True)
#      elevation = models.FloatField(null=True, blank=True)
#      rast = gis_models.RasterField(srid=25833)
#      extent = gis_models.PolygonField(srid=25833, null=True, blank=True)

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
    

    
class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_userfields")
    name = models.CharField(max_length=255)
    creation_date = models.DateField(blank=True, default=now)
    geom_json = PolygonField(null=True)
    comment = models.TextField(null=True, blank=True)
    geom = gis_models.GeometryField(null=True, srid=4326)
    

    def __str__(self):
        return self.name
    
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



class ToolboxProject(models.Model):    
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="toolbox_projects")
    description = models.TextField(null=True, blank=True)
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    toolbox_type = models.ForeignKey(ToolboxType, on_delete=models.CASCADE)
    creation_date = models.DateField(blank=True, default=now)
    last_modified = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name
    
    def to_json(self):
        # Start with the project fields
        return {
            "id": self.id, # if self.id is not None else None,
            "name": self.name,
            "description": self.description,
            # 'userField': self.user_field.id,
            # 'toolbox_type': self.toolbox_type.name,
        }


######################### INJECTION ###########################

class InfiltrationProject(ToolboxProject):
    weighting = models.ForeignKey(SinkWeighting, on_delete=models.CASCADE, null=True)


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


class Wasserrueckhaltepotentiale(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326)
    typ = models.CharField(max_length=100, null=True)
    anmerkung = models.CharField(max_length=255, null=True)
    dokument1 = models.CharField(max_length=255, null=True)
    derzeitige_nutzung = models.CharField(max_length=255, null=True)
    quelle_1 = models.CharField(max_length=255, null=True)
    quelle_2 = models.CharField(max_length=255, null=True)
    quelle_3 = models.CharField(max_length=255, null=True)
    massnahmen_id = models.CharField(max_length=100, null=True)  
    gewaesserverwaltung = models.CharField(max_length=255, null=True)
    gewaesser_name = models.CharField(max_length=255, null=True)
    flaeche_m2 = models.FloatField(null=True)
    kartenquelle = models.CharField(max_length=255, null=True)

    def __str__(self):
         return self.gewaesser_name + ' ' + self.flaeche_m2
    

### ---- 2024-12-02 ---- ###

class Landuse(models.Model):
    name = models.CharField(max_length=50)
    name_v = models.CharField(max_length=50)
    
    sink_landuse_name = models.CharField(max_length=50, null=True)
    de = models.CharField(max_length=50, null=True, blank=True) # DE: Landnutzung
    en = models.CharField(max_length=50, null=True, blank=True) # EN: Landuse
    
    def __str__(self):
        return self.sink_landuse_name
    
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

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

    

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
    # landuse_1_fk = models.IntegerField(null=True, blank=True) 
    land_use_2 = models.CharField(max_length=100, null=True)
    landuse_2 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse_2')
    # landuse_2_fk = models.IntegerField(null=True, blank=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    landuse_3 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='sink_landuse_3')
    # landuse_3_fk = models.IntegerField(null=True, blank=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    soil_points = models.CharField(max_length=16, null=True, blank=True) # number of soil points
    index_feasibility = models.FloatField(null=True) # Eval of soil points
    hydrogeology_text = models.CharField(max_length=255, null=True, blank=True) # related table
    aquifer = models.ForeignKey('Aquifer', on_delete=models.DO_NOTHING, null=True, blank=True)
    index_hydrogeology = models.FloatField(null=True, blank=True)


    # def save(self, *args, **kwargs):
    #     if self.geom and not self.centroid:
    #         self.centroid = self.geom.centroid  # Auto-generate centroid
    #     super().save(*args, **kwargs)

    def to_json(self):
        return {
            "id": self.id,
            "depth": self.depth,
            "area": self.area,
            "volume": self.volume,
            "index_1": self.index_1,
            "index_2": self.index_2,
            "index_3": self.index_3,
            "land_use_1": self.land_use_1,
            "land_use_2": self.land_use_2,
            "land_use_3": self.land_use_3,
            "index_soil": self.index_soil,
            "shape_length": self.shape_length,
            "shape_area": self.shape_area,
            "index_feasibility": self.index_feasibility,
            "hydrogeology": self.hydrogeology,
            "index_hydrogeology": self.index_hydrogeology,
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
    # sink_type = models.CharField(max_length=100, null=True) # related table
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
    # land_use_1_fk = models.IntegerField(null=True, blank=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    landuse_2 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_2')
    # land_use_2_fk = models.IntegerField(null=True, blank=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    landuse_3 = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True, related_name='enlarged_sink_landuse_3')
    # landuse_3_fk = models.IntegerField(null=True, blank=True)
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

    def to_json(self):
        return {
            "id": self.id,
            "depth": round(self.depth, 2),
            "area": round(self.area, 2),
            "volume": round(self.volume, 2),
            "index_1": self.index_1,
            "index_2": self.index_2,
            "index_3": self.index_3,
            "land_use_1": self.land_use_1,
            "land_use_2": self.land_use_2,
            "land_use_3": self.land_use_3,
            "land_use_4": self.land_use_4,
            "index_soil": self.index_soil,
            "shape_length": self.shape_length,
            "shape_area": self.shape_area,
            "index_feasibility": self.index_feasibility,
            "hydrogeology": self.hydrogeology,
            "index_hydrogeology": self.index_hydrogeology,
        }

class Aquifer(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    name_de = models.CharField(max_length=255, null=True, blank=True)
    name_en = models.CharField(max_length=255, null=True, blank=True)
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
    

    
# Intersect of LandusMap and EnlargedSink
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

class FeasibilitySink(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    feasibility = models.ForeignKey(Feasibility, on_delete=models.DO_NOTHING, null=True)
    sink = models.ForeignKey(Sink, on_delete=models.DO_NOTHING, null=True)
    
    area = models.FloatField(null=True, blank=True)
    area_of_total = models.FloatField(null=True, blank=True)

class FeasibilityEnlargedSink(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    feasibility = models.ForeignKey(Feasibility, on_delete=models.DO_NOTHING, null=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.DO_NOTHING, null=True)

    area = models.FloatField(null=True, blank=True)
    area_of_total = models.FloatField(null=True, blank=True)
# Hydrology is the layer the sinks are intersected with for HydrologySinks and HydrologyEnlargedSinks. It is not used.
class Hydrogeology(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50, null=True)
    aquifer = models.CharField(max_length=150, null=True)
    index = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()


# splits some sinks into two categories
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


# for enlarged sinks
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




'''
Sollte nicht Ziel der Toolbox sein, den User:innen zwar den kürzesten Weg zu zeigen, und dennoch die Möglichkeit zur Verschiebung der Ein- und Auslasspunkte zu überlassen?
Nach welchen Krterien wurden diese PUNKTE gefunden? Wie werden passende Wasserzuleiter gefunden? Könnte man nicht ggf. einen anderen Zuleiter finden?
Wird das Gefälle bisher berücksichtigt?
'''
