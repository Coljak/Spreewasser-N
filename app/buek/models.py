from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point




class BulkDensityClass(models.Model):
    bulk_density_class = models.CharField(null=True, blank=True)
    raw_density_g_per_cm3 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.bulk_density_class
    
    class Meta:
        db_table = 'buek_bulk_density_class'

class Ka5TextureClass(models.Model):
    ka5_soiltype = models.CharField(max_length=255, null=True, blank=True)
    sand = models.FloatField(null=True, blank=True)
    clay = models.FloatField(null=True, blank=True)
    silt = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.ka5_soiltype
  
    class Meta:
        db_table = 'buek_ka5_texture_class'

# Create your models here.
class CapillaryRise(models.Model):
    soil_type = models.CharField(max_length=255, null=True, blank=True)
    ka5textureclass = models.ForeignKey(
        'Ka5TextureClass', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    distance = models.IntegerField(null=True, blank=True)
    capillary_rate = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'buek_capillary_rise'
    
class HumusClass(models.Model):
    humus_class = models.CharField(max_length=255, null=True, blank=True)
    corg = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.humus_class
           
    class Meta:
        db_table = 'buek_humus_class'

    
class PHClass(models.Model):
    ph_class = models.CharField(max_length=255, null=True, blank=True)
    ph_lower_value = models.FloatField(null=True, blank=True)
    ph_upper_value = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.ph_class
     
    class Meta:
        db_table = 'buek_ph_class'


class BuekPolygon(models.Model):
    polygon_id = models.BigIntegerField(primary_key=True)
    bgl = models.CharField(max_length=80, null=True, blank=True)
    symbol = models.CharField(max_length=80, null=True, blank=True)
    legende = models.CharField(max_length=200, null=True, blank=True)
    def __str__(self):    
        return 'Polygon ' + str(self.polygon_id)
    
    class Meta:
        db_table = 'buek_polygon'
   
class Buek200(models.Model):  
    id = models.AutoField(primary_key=True)
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    hinweis = models.CharField(max_length=91, null=True, blank=True)
    shape_area = models.FloatField()
    shape_leng = models.FloatField()
    geom = gis_models.MultiPolygonField(srid=4326)

    def __str__(self):
        return '  Polygon_id ' + str(self.polygon_id)
    @classmethod
    def get_polygon_id_by_lat_lon(cls, lat, lon):
        """
        Returns the polygon_id of the Buek200 polygon that contains the given lat and lon.
        """
        return cls.objects.filter(geom__contains=Point(lon, lat)).first().polygon_id

    
class CorineLandCover2018(models.Model):
    '''
    CLC 5 classes. For simplicity not completely normalized.
    '''
    label_level_1 = models.CharField(max_length=255, null=True, blank=True)
    label_level_2 = models.CharField(max_length=255, null=True, blank=True)
    label_level_3 = models.CharField(max_length=255, null=True, blank=True)
    label_de = models.CharField(max_length=255, null=True, blank=True)
    corine_landcover_code = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.corine_landcover_code)
    
    class Meta:
        db_table = 'buek_corine_land_cover_2018'

class SoilProfile(models.Model):
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    legacy_gen_id = models.IntegerField(null=True, blank=True)
    system_unit = models.CharField(max_length=255, null=True, blank=True)
    legacy_bodsysteinh = models.CharField(max_length=255, null=True, blank=True)
    legacy_bodtyp = models.CharField(max_length=255, null=True, blank=True)
    legacy_bo_subtyp = models.CharField(max_length=255, null=True, blank=True)
    legacy_bo_subtyp_txt = models.CharField(max_length=255, null=True, blank=True)
    area_percentage = models.IntegerField(null=True, blank=True)
    landusage = models.CharField(max_length=255, null=True, blank=True)
    corine_landcover_2018 = models.ForeignKey(CorineLandCover2018, on_delete=models.CASCADE, null=True, blank=True)
    landusage_corine_code = models.IntegerField(null=True, blank=True)
    soil_profile_no = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return 'soil_profile ' + str(self.id) 
    
    def get_all_horizons(self):
        return SoilProfileHorizon.objects.filter(soilprofile=self).order_by('horizont_nr')
    
    def get_all_horizons_json(self):
        hors = SoilProfileHorizon.objects.filter(soilprofile=self).order_by('horizont_nr')
        return [horizon.to_json() for horizon in hors]
    

    def get_monica_horizons_json(self):
        # TODO this is working but could use refactoring: the msg is not used
        """
        Invalid horizons are filled with the information of the next valid horizon.
        """
        horizons = list(SoilProfileHorizon.objects.filter(soilprofile=self, obergrenze_m__gte=0).order_by('horizont_nr'))
       
        msg = None
        hors = []
        # valid_horizon = False
        for i in range(len(horizons)):

            if not horizons[i].ka5_texture_class:
                if i < len(horizons) - 1:
                    horizons[i+1].obergrenze_m = horizons[i].obergrenze_m
                    msg = "Warning: Profile modified due to lacking ka5 texture class"
                    
                else:
                    horizons[i-1].untergrenze_m = horizons[i].untergrenze_m
                    msg = "Warning: Last horizon modified due to lacking ka5 texture class"
               
        for i in range(len(horizons)):
            if horizons[i].ka5_texture_class:
                hors.append(horizons[i].to_json())

        return hors, msg
    
    def get_horizons_json(self):
        horizons =  SoilProfileHorizon.objects.filter(soilprofile=self)
        horizons = horizons.filter(obergrenze_m__gte=0).order_by('horizont_nr')

        return [horizon.to_json() for horizon in horizons]

    class Meta:
        db_table = 'buek_soil_profile'
        
                                                                 
class SoilProfileHorizon(models.Model):
    soilprofile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, null=True, blank=True)
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
    # carbonatgehalt = models.CharField(null=True, blank=True)
    gefuege = models.CharField(max_length=255, null=True, blank=True)
    torfarten = models.CharField(max_length=255, null=True, blank=True)
    # zersetzungsstufe = models.CharField(max_length=255, null=True, blank=True)
    substanzvolumen = models.CharField(max_length=255, null=True, blank=True)
    # trockenrohdichte
    bulk_density_class = models.ForeignKey(BulkDensityClass, on_delete=models.CASCADE, null=True, blank=True)
    ka5_texture_class = models.ForeignKey(Ka5TextureClass, on_delete=models.CASCADE, null=True, blank=True)
    # humus
    humus_class = models.ForeignKey(HumusClass, on_delete=models.CASCADE, null=True, blank=True)
    # bodenaciditaet 
    ph_class = models.ForeignKey(PHClass, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return super().__str__() + ' soilprofile_id: ' + str(self.soilprofile_id) + ' horizont_nr: ' + str(self.horizont_nr)
    # TODO pH value is a range - how to use it
    # TODO Sceleton fraction 0-1, soil stone content
    def to_json(self):
        # TODO: can Monica actually handle the NULL values as '' or []?
        monica_json = {
            'Thickness': [round((self.untergrenze_m - self.obergrenze_m), 2), "m"],
            'Sand': [round(self.ka5_texture_class.sand, 2) * 100, "%"] if self.ka5_texture_class else [],
            'Clay': [round(self.ka5_texture_class.clay, 2) * 100, "%"] if self.ka5_texture_class else [],
            'pH': round(((self.ph_class.ph_lower_value + self.ph_class.ph_upper_value) / 2), 2) if self.ph_class else '',
            # 'Sceleton': soil stone content, a fraction between 0 and 1
            # 'Lambda': soil water conductivity coefficient
            # 'FieldCapacity':  	field capacity
            # 'PoreVolume': 	m3 m-3 (fraction [0-1]) 	saturation
            # 'PermanentWiltingPoint': 	m3 m-3 (fraction [0-1]) 	permanent wilting point
            'KA5TextureClass': self.ka5_texture_class.ka5_soiltype if self.ka5_texture_class else '',
            # 'SoilAmmonium': [self.soil_ammonium, "mg kg-1"],
            # 'SoilNitrate': 	kg NO3-N m-3 	initial soil nitrate content
            # 'CN': 		soil C/N ratio
            'SoilRawDensity': [self.bulk_density_class.raw_density_g_per_cm3 * 1000, "kg m-3"] if self.bulk_density_class else [],
            #  OR SoilBulkDensity 	kg m-3 	soil bulk density
            'SoilOrganicCarbon': [round(self.humus_class.corg, 2), "%"] if self.humus_class else [],
            # TODO wiki: SoilOrganicCarbon 	% [0-100] ([kg C kg-1] * 100)  a percentage between 0 and 100 BUT it seems to be a percenteage
            # OR 'SoilOrganicMatter': 	kg OM kg-1 (fraction [0-1]) 	soil organic matter
            # 'SoilMoisturePercentFC': % [0-100] 	initial soil moisture in percent of field capacity
        }
  
        return monica_json
    
    class Meta:
        db_table = 'buek_soil_profile_horizon'

class MapSoilCLC(models.Model):
    """
    This data applies to the Vector as well as the Raster files of the BUEK 200/CLC 2018 dataset.
    It contains a reference to the original BGR Buek 200 (tkle_nr) that is equivalent to the polygon_id in the BuekPolygon model.
    Though in this dataset the polygon_id doesn't necessarily reference the original Buek Polygon,
    the tkle_nr of the polygon is the original identifier of the polygon. Where .
    """
    tkle_nr = models.IntegerField(null=True, blank=True)
    polygon = models.ForeignKey(BuekPolygon, on_delete=models.CASCADE, null=True, blank=True)
    corine_landcover_code = models.ForeignKey(CorineLandCover2018, on_delete=models.CASCADE, null=True, blank=True)
    water = models.BooleanField(default=False)
    soilprofile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='soilprofile')
    clc_code = models.IntegerField(null=True, blank=True)
    bias_21_soilprofile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='bias_21_soilprofile')
    bias_21_clc_code = models.IntegerField(null=True, blank=True)
    bias_23_soilprofile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='bias_23_soilprofile')
    bias_23_clc_code = models.IntegerField(null=True, blank=True)
    bias_31_soilprofile = models.ForeignKey(SoilProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='bias_31_soilprofile')
    bias_31_clc_code = models.IntegerField(null=True, blank=True)
    geom = gis_models.PolygonField(srid=4326)
    def __str__(self):
        return 'Polygon ' + str(self.polygon_id)# + ' CLC2018 ' + str(self.corine_landcover_code.corine_landcover_code) + str(self.corine_landcover_code.label_de)

    
    class Meta:
        db_table = 'buek_map_soil_clc'



