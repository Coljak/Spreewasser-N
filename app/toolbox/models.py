from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
from django.utils.timezone import now
from buek.models import CorineLandCover2018

class ToolboxType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

# class Project(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.CharField(max_length=255)
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#     geom = gis_models.MultiPolygonField(srid=25833, null=True)

#     def __str__(self):
#         return self.name

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


class UserProject(models.Model):    
    name = models.CharField(max_length=255)
    user_field = models.ForeignKey(UserField, on_delete=models.CASCADE, related_name="toolbox_userprojects")
    comment = models.TextField(null=True, blank=True)
    calculation_start_date = models.DateField(null=True, blank=True)
    calculation_end_date = models.DateField(null=True, blank=True)
    calculation = models.JSONField(null=True, blank=True)
    creation_date = models.DateField(blank=True, default=now)

    def __str__(self):
        return self.name

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
    

# # DE: Dränung
# class OutlineDrainage(gis_models.Model):
#     name = models.CharField(max_length=64, blank=True, null=True)
#     geom = gis_models.MultiPolygonField('Drainage')

#     def __str__(self):
#                 return self.name



class SinksWithLandUseAndSoilProperties(models.Model): # DELETE
    geom = gis_models.MultiPolygonField(srid=4326)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    landuse_1 = models.CharField(max_length=100, null=True)
    landuse_2 = models.CharField(max_length=100, null=True)
    landuse_3 = models.CharField(max_length=100, null=True)
    landuse_1_percent = models.FloatField(null=True)
    landuse_2_percent = models.FloatField(null=True)
    landuse_3_percent = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    forest_deciduous_trees = models.FloatField(null=True, default=0)
    heath = models.FloatField(null=True, default=0)
    orchard_meadow = models.FloatField(null=True, default=0)
    vegetation = models.FloatField(null=True, default=0)
    grassland = models.FloatField(null=True, default=0)
    agricultural_area_without_information = models.FloatField(null=True, default=0)
    farmland = models.FloatField(null=True, default=0)
    woody_area = models.FloatField(null=True, default=0)
    forest_conifers = models.FloatField(null=True, default=0)
    forest_conifers_and_deciduous_trees = models.FloatField(null=True, default=0)

class SinksWithLandUseAndSoilPropertiesSimplified(models.Model): # DELETE
    geom = gis_models.MultiPolygonField(srid=4326, default=None)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    landuse_1 = models.CharField(max_length=100, null=True)
    landuse_2 = models.CharField(max_length=100, null=True)
    landuse_3 = models.CharField(max_length=100, null=True)
    landuse_1_percent = models.FloatField(null=True)
    landuse_2_percent = models.FloatField(null=True)
    landuse_3_percent = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    forest_deciduous_trees = models.FloatField(null=True, default=0)
    heath = models.FloatField(null=True, default=0)
    orchard_meadow = models.FloatField(null=True, default=0)
    vegetation = models.FloatField(null=True, default=0)
    grassland = models.FloatField(null=True, default=0)
    agricultural_area_without_information = models.FloatField(null=True, default=0)
    farmland = models.FloatField(null=True, default=0)
    woody_area = models.FloatField(null=True, default=0)
    forest_conifers = models.FloatField(null=True, default=0)
    forest_conifers_and_deciduous_trees = models.FloatField(null=True, default=0)

class SinksWithLandUseAndSoilPropertiesAsPoints(models.Model): # DELETE
    geom = gis_models.PointField(srid=4326)
    objectid = models.IntegerField(null=True)
    fid_sink = models.IntegerField(null=True)
    depth_sink = models.FloatField(null=True)
    area_sink = models.FloatField(null=True)
    index_sink = models.FloatField(null=True)
    index_si_1 = models.FloatField(null=True)
    landuse_1 = models.CharField(max_length=100, null=True)
    landuse_2 = models.CharField(max_length=100, null=True)
    landuse_3 = models.CharField(max_length=100, null=True)
    landuse_1_percent = models.FloatField(null=True)
    landuse_2_percent = models.FloatField(null=True)
    landuse_3_percent = models.FloatField(null=True)
    index_soil = models.FloatField(null=True)
    forest_deciduous_trees = models.FloatField(null=True, default=0)
    heath = models.FloatField(null=True, default=0)
    orchard_meadow = models.FloatField(null=True, default=0)
    vegetation = models.FloatField(null=True, default=0)
    grassland = models.FloatField(null=True, default=0)
    agricultural_area_without_information = models.FloatField(null=True, default=0)
    farmland = models.FloatField(null=True, default=0)
    woody_area = models.FloatField(null=True, default=0)
    forest_conifers = models.FloatField(null=True, default=0)
    forest_conifers_and_deciduous_trees = models.FloatField(null=True, default=0)


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

class Sink(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    feasibility_sinks_index = models.FloatField(null=True)

# checked/copied
class DataEnlargedSinks(models.Model): 
    fid_sink = models.IntegerField(null=True) # primary_key=True does not work - DUPLICATE KEYS!
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    depth = models.FloatField(null=True)
    area = models.FloatField(null=True)
    nat_length = models.FloatField(null=True)
    por_length = models.FloatField(null=True)
    con_length = models.FloatField(null=True)
    sink_type = models.CharField(max_length=100, null=True) # related table
    volume = models.FloatField(null=True)
    vol_ba_con = models.FloatField(null=True)
    gained_vol =  models.FloatField(null=True)
    con_eff = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)
    land_use_1 = models.CharField(max_length=100, null=True)
    land_use_2 = models.CharField(max_length=100, null=True)
    land_use_3 = models.CharField(max_length=100, null=True)
    land_use_4 = models.CharField(max_length=100, null=True)
    index_soil = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)
    feasibilty_enlarged_sinks_index = models.FloatField(null=True)

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

class HydrogeologyEnlargedSinks(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    aq_complex = models.CharField(max_length=50)
    aquifer = models.CharField(max_length=150)
    fid_sink = models.IntegerField(null=True)
    index_sink = models.FloatField(null=True)
    shape_length = models.FloatField(null=True)
    shape_area = models.FloatField(null=True)

class LandUse(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)

    name = models.CharField(max_length=50)
    name_v = models.CharField(max_length=50)

    index_land = models.IntegerField()
    corine_1 = models.IntegerField(null=True)
    corine_2 = models.IntegerField(null=True)
    corine_3 = models.IntegerField(null=True)
    corine_land_cover = models.ForeignKey(CorineLandCover2018, on_delete=models.DO_NOTHING, null=True)

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


class SoilProperties(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    nitrate = models.CharField(max_length=50)
    c_nitrate = models.IntegerField()
    waterlog = models.CharField(max_length=50)
    c_waterlog = models.IntegerField()
    depth_gw = models.CharField(max_length=50)
    c_depth_gw = models.FloatField()
    hycon_1m = models.CharField(max_length=50)
    c_hycon_1m = models.FloatField()
    w_hycon_1m = models.FloatField()
    hycon_2m = models.CharField(max_length=50)
    c_hycon_2m = models.FloatField()
    w_hycon_2m = models.FloatField()
    fiecap = models.CharField(max_length=50)
    c_fiecap = models.FloatField()
    w_fiecap = models.FloatField()
    hydro = models.CharField(max_length=100)
    c_hydro = models.FloatField()
    w_hydro = models.FloatField()
    ag_soil = models.CharField(max_length=50)
    c_ag_soil = models.FloatField()
    w_ag_soil = models.FloatField()
    wet_gras = models.CharField(max_length=50)
    c_wet_gras = models.FloatField()
    w_wet_gras = models.FloatField()
    ag_use = models.CharField(max_length=50)
    c_land_use = models.CharField()
    c_suit = models.IntegerField()
    c_suit_gw = models.FloatField()
    w_suit_gw = models.FloatField()
    c_soil_1 = models.FloatField()
    c_soil_2 = models.FloatField()
    c_soil_3 = models.FloatField()
    w_soil = models.FloatField()
    index_soil = models.FloatField()
    shape_length = models.FloatField()
    shape_area = models.FloatField()

class Lakes(models.Model):
    geom = gis_models.MultiPolygonField(srid=25833)
    centroid = gis_models.PointField(srid=25833, null=True, blank=True)
    shape_length = models.FloatField()
    shape_area = models.FloatField()
    # id_lake = models.IntegerField()
    min_sv = models.FloatField()
    mean_sv = models.FloatField()
    max_sv = models.FloatField()
    plus_days = models.FloatField()

class Stream(models.Model):
    geom = gis_models.MultiLineStringField(srid=25833)
    shape_length = models.FloatField()
    # id_source = models.IntegerField()
    min_sv = models.FloatField()
    mean_sv = models.FloatField()
    max_sv = models.FloatField()
    plus_days = models.FloatField()

class ExtractionPointsSinks(models.Model):
    geom = gis_models.PointField(srid=25833)
    sink = models.ForeignKey(Sink, on_delete=models.CASCADE, null=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True)
    lake = models.ForeignKey(Lakes, on_delete=models.CASCADE, null=True)
    distance = models.FloatField(null=True)
    min_sv = models.FloatField(null=True)
    mean_sv = models.FloatField(null=True)
    max_sv = models.FloatField(null=True)
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
    min_sv = models.FloatField(null=True)
    mean_sv = models.FloatField(null=True)
    max_sv = models.FloatField(null=True)
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
    min_sv = models.FloatField(null=True)
    mean_sv = models.FloatField(null=True)
    max_sv = models.FloatField(null=True)
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
    min_sv = models.FloatField(null=True)
    mean_sv = models.FloatField(null=True)
    max_sv = models.FloatField(null=True)
    vol_sink = models.FloatField(null=True)
    index_1 = models.FloatField(null=True)
    weight_1 = models.FloatField(null=True)
    index_2 = models.FloatField(null=True)
    weight_2 = models.FloatField(null=True)
    index_3 = models.FloatField(null=True)

    
class LandUsage(models.Model):
     name = models.CharField(max_length=100)



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
# 	mean_sv float8 NOT NULL,
# 	max_sv float8 NOT NULL,
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
# 	mean_sv float8 NULL,
# 	max_sv float8 NULL,
# 	vol_sink float8 NULL,
# 	index_1 float8 NULL,
# 	weight_1 float8 NULL,
# 	index_2 float8 NULL,
# 	weight_2 float8 NULL,
# 	index_3 float8 NULL,
# 	CONSTRAINT toolbox_inletpointssinks_pkey PRIMARY KEY (id)
# );
# CREATE INDEX toolbox_inletpointssinks_geom_e5700fef_id ON public.toolbox_inletpointssinks USING gist (geom);