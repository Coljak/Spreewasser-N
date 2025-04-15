from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
from django.utils.timezone import now
from buek.models import CorineLandCover2018
from django.contrib.gis.db.models.functions import Transform
class ToolboxType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    



class DigitalElevationModel10(models.Model):
     name = models.CharField(max_length=100, null=True, blank=True)
     elevation = models.FloatField(null=True, blank=True)
     rast = gis_models.RasterField(srid=25833)
     extent = gis_models.PolygonField(srid=25833, null=True, blank=True)

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


class Infiltration(models.Model):
    weighting = models.ForeignKey(SinkWeighting, on_delete=models.CASCADE, null=True)


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
    buek_corine_land_cover = models.ForeignKey(CorineLandCover2018, on_delete=models.DO_NOTHING, null=True, related_name='buek_corine_land_cover')
    clc = models.IntegerField(null=True, blank=True)

# landuse_dissolve
class LandUseMap(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)

    name = models.CharField(max_length=50)
    name_v = models.CharField(max_length=50)

    index_land = models.IntegerField()
    corine_1 = models.IntegerField(null=True)
    corine_2 = models.IntegerField(null=True)
    corine_3 = models.IntegerField(null=True)
    # corine_land_cover = models.ForeignKey(CorineLandCover2018, on_delete=models.DO_NOTHING, null=True)
    code_18 = models.CharField(max_length=4, null=True)
    # buek_corine_land_cover = models.ForeignKey(CorineLandCover2018, on_delete=models.DO_NOTHING, null=True, related_name='buek_corine_land_cover')
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)
class LandUse4326(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)

    name = models.CharField(max_length=50)
    name_v = models.CharField(max_length=50)

    index_land = models.IntegerField()
    corine_1 = models.IntegerField(null=True)
    corine_2 = models.IntegerField(null=True)
    corine_3 = models.IntegerField(null=True)
    corine_land_cover = models.ForeignKey(CorineLandCover2018, on_delete=models.DO_NOTHING, null=True)

class Stream4326(models.Model):
    geom = gis_models.MultiLineStringField(srid=4326)
    shape_length = models.FloatField()
    # id_source = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()
    simple_geom = gis_models.LineStringField(srid=4326, null=True, blank=True)



class Stream(models.Model):
    geom = gis_models.MultiLineStringField(srid=25833)
    shape_length = models.FloatField()
    # id_source = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()
    
    def save_as_4326(self):
        transformed_geom = self.geom.transform(4326, clone=True) if self.geom else None

        Stream4326.objects.create(
            geom = transformed_geom,
            shape_length = self.shape_length,
            min_surplus_volume = self.min_surplus_volume,
            mean_surplus_volume = self.mean_surplus_volume,
            max_surplus_volume = self.max_surplus_volume,
            plus_days = self.plus_days
        )

class Lake4326(models.Model):
    geom = gis_models.MultiPolygonField(srid=4326)
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

    
class Lake(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    shape_length = models.FloatField()
    shape_area = models.FloatField()
    # id_lake = models.IntegerField()
    min_surplus_volume = models.FloatField()
    mean_surplus_volume = models.FloatField()
    max_surplus_volume = models.FloatField()
    plus_days = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

    def save_as_4326(self):
        transformed_geom = self.geom.transform(4326, clone=True) if self.geom else None
        transformed_centroid = self.centroid.transform(4326, clone=True) if self.centroid else None

        Lake4326.objects.create(
            geom = transformed_geom,
            centroid = transformed_centroid,
            shape_length = self.shape_length,
            shape_area = self.shape_area,
            min_surplus_volume = self.min_surplus_volume,
            mean_surplus_volume = self.mean_surplus_volume,
            max_surplus_volume = self.max_surplus_volume,
            plus_days = self.plus_days
        )



class Sink4326(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = gis_models.MultiPolygonField(srid=4326)
    geom_simplified = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    feasibility_sinks_index = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

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
            "feasibility_sinks_index": self.feasibility_sinks_index,
        }
    
    

class Sink(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    feasibility_sinks_index = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

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
            "feasibility_sinks_index": self.feasibility_sinks_index,
        }
    def save_as_4326(self):
        transformed_geom = self.geom.transform(4326, clone=True) if self.geom else None
        transformed_centroid = self.centroid.transform(4326, clone=True) if self.centroid else None

        Sink4326.objects.create(
            id = self.id,
            geom = transformed_geom,
            centroid = transformed_centroid,
            depth = self.depth,
            area = self.area,
            volume = self.volume,
            shape_length = self.shape_length,
            index_1 = self.index_1,
            index_2 = self.index_2,
            index_3 = self.index_3,
            land_use_1 = self.land_use_1,
            land_use_2 = self.land_use_2,
            land_use_3 = self.land_use_3,
            land_use_1_percentage = self.land_use_1_percentage,
            land_use_2_percentage = self.land_use_2_percentage,
            land_use_3_percentage = self.land_use_3_percentage,
            index_soil = self.index_soil,
            feasibility_sinks_index = self.feasibility_sinks_index,

        )

class EnlargedSink4326(models.Model): 
    id = models.IntegerField(primary_key=True) # former fid_sink
    geom = gis_models.MultiPolygonField(srid=4326)
    geom_simplified = gis_models.PolygonField(srid=4326, null=True, blank=True)
    centroid = gis_models.PointField(srid=4326, null=True, blank=True)
    extractionpoint = models.ForeignKey('ExtractionPointsEnlargedSinks', on_delete=models.DO_NOTHING, null=True)
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
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    land_use_4 = models.CharField(max_length=100, null=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    land_use_4_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)


    feasibilty_enlarged_sinks_index = models.FloatField(null=True)


class EnlargedSink(models.Model): 
    id = models.IntegerField(primary_key=True) # former fid_sink
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    extractionpoint = models.ForeignKey('ExtractionPointsEnlargedSinks', on_delete=models.DO_NOTHING, null=True)
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
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    land_use_4 = models.CharField(max_length=100, null=True)
    land_use_1_percentage = models.FloatField(null=True)
    land_use_2_percentage = models.FloatField(null=True)
    land_use_3_percentage = models.FloatField(null=True)
    land_use_4_percentage = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)

    feasibilty_enlarged_sinks_index = models.FloatField(null=True)


    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

    def save_as_4326(self):
        transformed_geom = self.geom.transform(4326, clone=True) if self.geom else None
        transformed_centroid = self.centroid.transform(4326, clone=True) if self.centroid else None

        # ep_transformed = self.extractionpoint.ep_geom.transform(4326, clone=True) if self.extractionpoint.ep_geom else None

        EnlargedSink4326.objects.create(
            id = self.id,
            geom = transformed_geom,
            centroid = transformed_geom.centroid,
            depth = self.depth,
            area = self.area,
            nat_length = self.nat_length,
            por_length = self.por_length,
            con_length = self.con_length,
            # sink_type = models.CharField(max_length=100, null=True) # related table
            constructed_sink = self.constructed_sink,
            volume = self.volume,
            volume_construction_barrier = self.volume_construction_barrier,
            volume_gained =  self.volume_gained,
            construction_efficiciency = self.construction_efficiciency, 
            index_1 = self.index_1,
            index_2 = self.index_2,
            index_3 = self.index_3,
            land_use_1 = self.land_use_1,
            land_use_2 = self.land_use_2,
            land_use_3 = self.land_use_3,
            land_use_4 = self.land_use_4,
            land_use_1_percentage = self.land_use_1_percentage,
            land_use_2_percentage = self.land_use_2_percentage,
            land_use_3_percentage = self.land_use_3_percentage,
            land_use_4_percentage = self.land_use_4_percentage,
            index_soil = self.index_soil,
            shape_length = self.shape_length,
            shape_area = self.shape_area,

            feasibilty_enlarged_sinks_index = self.feasibilty_enlarged_sinks_index,
            # ExtractionPointsEnlargedSinks ep
            # ep_geom = ep_transformed,
            # ep_fid_sink = self.ep_fid_sink,
            # ep_id_source = self.ep_id_source,
            # ep_id_lake = self.ep_id_lake,
            # ep_distance = self.ep_distance,
            # ep_min_surplus_volume = self.ep_min_surplus_volume,
            # ep_mean_surplus_volume = self.ep_mean_surplus_volume,
            # ep_max_surplus_volume = self.ep_max_surplus_volume,
            # ep_vol_sink = self.ep_vol_sink,
            # ep_index_1 = self.ep_index_1,
            # ep_weight_1 = self.ep_weight_1,
            # ep_index_2 = self.ep_index_2,
            # ep_weight_2 = self.ep_weight_2,
            # ep_index_3 = self.ep_index_3
        )

class Feasability(models.Model): # soilstuff
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    veg_fe = models.CharField(max_length=100, null=True)
    land_use = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    fie_as_num = models.FloatField(null=True)
    index = models.FloatField(null=True)

# class FeasabilitySinks(models.Model):
#     fid_sink = models.IntegerField(null=True)
#     geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
#     centroid = gis_models.PointField(srid=25833, null=True, blank=True)
#     shape_length = models.FloatField(null=True)
#     shape_area = models.FloatField(null=True)
#     index = models.FloatField(null=True)


class FeasabilityEnlargedSinks(models.Model):
    fid_sink = models.IntegerField(null=True)
    geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    index = models.FloatField(null=True)
     
# WHERE DID THID COME FROM?
# class Aquifer(models.Model):
#     name = models.CharField(max_length=255)
#     geom = gis_models.MultiPolygonField(srid=25833, null=True, blank=True)
#     centroid = gis_models.PointField(srid=25833, null=True, blank=True)

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
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

class HydrogeologyEnlargedSinks(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50)
    aquifer = models.CharField(max_length=150)
    # fid_sink = models.IntegerField(null=True)
    index_sink = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    enlarged_sink = models.ForeignKey(EnlargedSink, on_delete=models.CASCADE, null=True) # fid_sink

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)


# for enlarged sinks
class SinkEmbankment(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    fid_sink = models.IntegerField()
    height = models.FloatField()
    plat_width = models.FloatField()
    volume = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

class FieldCapacityClass(models.Model):
    upper_limit = models.FloatField(null=True)
    lower_limit = models.FloatField(null=True)
    class_name = models.CharField(max_length=50, null=True)
    rating_index = models.FloatField()

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

class Soil(models.Model):
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
    nitrate_contamination = models.BooleanField(default=False)
    waterlog = models.BooleanField(default=False)
    groundwater_distance = models.ForeignKey(GroundWaterDistanceClass, on_delete=models.DO_NOTHING, null=True)
    hydraulic_conductivity_1m_rating = models.FloatField()
    hydraulic_conductivity_2m_rating = models.FloatField()
    fieldcapacity = models.ForeignKey(FieldCapacity, on_delete=models.DO_NOTHING, null=True)
    hydromorphy = models.ForeignKey(Hydromorphy, on_delete=models.DO_NOTHING, null=True)
    soil = models.ForeignKey(Soil, on_delete=models.DO_NOTHING, null=True)
    wet_gras = models.CharField(max_length=50)
    c_wet_gras = models.FloatField()
    wet_grassland = models.ForeignKey(WetGrassland, on_delete=models.DO_NOTHING, null=True)
    agricultural_landuse = models.ForeignKey(AgriculturalLanduse, on_delete=models.DO_NOTHING, null=True)
    c_suit = models.IntegerField()
    c_suit_gw = models.FloatField()
    c_soil_1 = models.FloatField()
    c_soil_2 = models.FloatField()
    c_soil_3 = models.FloatField()
    index_soil = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()
    landuse = models.ForeignKey(Landuse, on_delete=models.DO_NOTHING, null=True)

    def save(self, *args, **kwargs):
        if self.geom and not self.centroid:
            self.centroid = self.geom.centroid  # Auto-generate centroid
        super().save(*args, **kwargs)

    def get_soil_suitability(
            self, 
            weight_general=.2, 
            weight_soil=.8, 
            **kwargs
            ):
        if not kwargs:
            weight_field_capacity = .33
            weight_hydro_conduct_1m=.33
            weight_hydro_conduct_2m=.33
            weight_hydromorphy=.33
            weight_soil_index=.33 # w_ag_soil
            weight_soil_moisture_grassland = .25
            if self.agricultural_landuse.name == 'grassland':
                weight_field_capacity = .25
                weight_soil_index = .25
                weight_hydromorphy=.25

        bool_general = (not self.nitrate_contamination) and (not self.waterlog)
        # print('bool_general', bool_general)
        index_soil = weight_field_capacity * self.fieldcapacity.rating_index + \
            weight_hydro_conduct_1m * self.hydraulic_conductivity_1m_rating + \
            weight_hydro_conduct_2m * self.hydraulic_conductivity_2m_rating + \
            weight_hydromorphy * self.hydromorphy.rating_index + \
            weight_soil_index * self.soil.rating_index + \
            weight_soil_moisture_grassland * self.wet_grassland.rating_index

        # print('index_soil', index_soil)
        return round(((weight_general * self.groundwater_distance.rating_index + weight_soil * index_soil) * bool_general), 2)

        




class ExtractionPointsSinks(models.Model):
    geom = gis_models.PointField(srid=25833)
    sink = models.ForeignKey(Sink, on_delete=models.CASCADE, null=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True)
    lake = models.ForeignKey(Lake, on_delete=models.CASCADE, null=True)
    distance = models.FloatField(null=True)
    min_surplus_volume = models.FloatField(null=True)
    mean_surplus_volume = models.FloatField(null=True)
    max_surplus_volume = models.FloatField(null=True)
    vol_sink = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    weight_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    weight_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)

class ExtractionPointsEnlargedSinks(models.Model):
    geom = gis_models.PointField(srid=25833)
    fid_sink = models.IntegerField(null=True)
    id_source = models.IntegerField(null=True)
    id_lake = models.IntegerField(null=True)
    distance = models.FloatField(null=True)
    min_surplus_volume = models.FloatField(null=True)
    mean_surplus_volume = models.FloatField(null=True)
    max_surplus_volume = models.FloatField(null=True)
    vol_sink = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    weight_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    weight_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)

class InletPointsSinks(models.Model):
    geom = gis_models.PointField(srid=25833)
    fid_sink = models.IntegerField(null=True)
    id_source = models.IntegerField(null=True)
    id_lake = models.IntegerField(null=True)
    distance = models.FloatField(null=True)
    min_surplus_volume = models.FloatField(null=True)
    mean_surplus_volume = models.FloatField(null=True)
    max_surplus_volume = models.FloatField(null=True)
    vol_sink = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    weight_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    weight_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)

class InletPointsEnlargedSinks(models.Model):
    geom = gis_models.PointField(srid=25833)
    fid_sink = models.IntegerField(null=True)
    id_source = models.IntegerField(null=True)
    id_lake = models.IntegerField(null=True)
    distance = models.FloatField(null=True)
    min_surplus_volume = models.FloatField(null=True)
    mean_surplus_volume = models.FloatField(null=True)
    max_surplus_volume = models.FloatField(null=True)
    vol_sink = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    weight_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    weight_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)

    

'''
Sollte nicht Ziel der Toolbox sein, den User:innen zwar den kürzesten Weg zu zeigen, und dennoch die Möglichkeit zur Verschiebung der Ein- und Auslasspunkte zu überlassen?
Nach welchen Krterien wurden diese PUNKTE gefunden? Wie werden passende Wasserzuleiter gefunden? Könnte man nicht ggf. einen anderen Zuleiter finden?
Wird das Gefälle bisher berücksichtigt?
'''


# -- public.toolbox_lakes definition

# -- Drop table

# -- DROP TABLE public.toolbox_lakes;

# CREATE TABLE public.toolbox_lakes (
# 	geom public.geometry(multipolygon, 25833) NOT NULL,
# 	shape_length float8 NOT NULL,
# 	shape_area float8 NOT NULL,
# 	id int8 GENERATED BY DEFAULT AS IDENTITY NOT NULL,
# 	min_sv float8 NOT NULL,
# 	mean_surplus_volume float8 NOT NULL,
# 	max_surplus_volume float8 NOT NULL,
# 	plus_days float8 NOT NULL,
# 	centroid public.geometry(point, 25833) NULL
# );
# CREATE INDEX toolbox_datalakes_centroid_756134a7_id ON public.toolbox_lakes USING gist (centroid);
# CREATE INDEX toolbox_datalakes_geom_534757a1_id ON public.toolbox_lakes USING gist (geom);


# CREATE TABLE public.toolbox_inletpointssinks (
# 	id int8 GENERATED BY DEFAULT AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
# 	geom public.geometry(point, 25833) NOT NULL,
# 	fid_sink int4 NULL,
# 	id_source int4 NULL,
# 	id_lake int4 NULL,
# 	distance float8 NULL,
# 	min_sv float8 NULL,
# 	mean_surplus_volume float8 NULL,
# 	max_surplus_volume float8 NULL,
# 	vol_sink float8 NULL,
# 	index_1 float8 NULL,
# 	weight_1 float8 NULL,
# 	index_2 float8 NULL,
# 	weight_2 float8 NULL,
# 	index_3 float8 NULL,
# 	CONSTRAINT toolbox_inletpointssinks_pkey PRIMARY KEY (id)
# );
# CREATE INDEX toolbox_inletpointssinks_geom_e5700fef_id ON public.toolbox_inletpointssinks USING gist (geom);