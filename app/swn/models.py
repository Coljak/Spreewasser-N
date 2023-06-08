"""
Database models.
"""

from email.policy import default
from statistics import mode

from django.db import models
from django.contrib.gis.db import models as gis_models
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField, GeometryField
#from user.models import User
from django.contrib.auth.models import User
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

# class UserInfo(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
#     def __str__(self):
#         return self.user.name

# moved to user
# class UserManager(BaseUserManager):
#     """Manager for users."""
#     def create_user(self, email, password=None, **extra_fields):
#         """Create, save and return a new user."""
#         if not email:
#             raise ValueError('User must have an email address.')
#         user = self.model(email=self.normalize_email(email), **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)

#         return user

#     def create_superuser(self, email, password):
#         """Create and return a new superuser."""
#         user = self.create_user(email, password)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)

#         return user

# moved to user
# class User(AbstractBaseUser, PermissionsMixin):
#     """User in the system."""
#     email = models.EmailField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
    
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = UserManager()

#     USERNAME_FIELD = 'email'

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
    #geom2 = models.GeometryField(null=True, srid=4326)
    

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

# ----------BUEK 200 data ------------------------------------------------
# class BuekData(models.Model):
#     nrkart = models.BigIntegerField(null=True)
#     polygon_id = models.BigIntegerField(null=True)
#     bgl = models.CharField(max_length=80, null=True)
#     symbol = models.CharField(max_length=80, null=True)
#     legende = models.CharField(max_length=200, null=True)
#     hinweis = models.CharField(max_length=86, null=True)
#     shape_area = models.FloatField(null=True)
#     shape_leng = models.FloatField(null=True)
#     geom = gis_models.MultiPolygonField(srid=4326)

#     def __str__(self):
#         return 'Buek200 NKART %s' % self.nrkart
    


# class SoilProfileAll(models.Model):
    
#     # polygon = models.ForeignKey(BuekData, on_delete = models.DO_NOTHING)
    
#     profile_id_in_polygon = models.IntegerField(null=True, blank=True)
#     range_percentage_of_area = models.CharField(max_length=56, null=True, blank=True)
#     avg_range_percentage_of_area = models.IntegerField(null=True, blank=True)
#     horizon_id = models.IntegerField(null=True, blank=True)
#     layer_depth = models.IntegerField(null=True, blank=True)
#     bulk_density = models.IntegerField(null=True, blank=True)
#     raw_density = models.IntegerField(null=True, blank=True)
#     soil_organic_carbon = models.FloatField(null=True, blank=True)
#     soil_organic_matter = models.IntegerField(null=True, blank=True)
#     ph = models.IntegerField(null=True, blank=True)
#     ka5_texture_class = models.CharField(max_length=56, null=True, blank=True)
#     sand = models.IntegerField(null=True, blank=True)
#     clay = models.IntegerField(null=True, blank=True)
#     silt = models.IntegerField(null=True, blank=True)
#     permanent_wilting_point = models.IntegerField(null=True, blank=True)
#     field_capacity = models.IntegerField(null=True, blank=True)
#     saturation = models.IntegerField(null=True, blank=True)
#     soil_water_conductivity_coefficient = models.IntegerField(null=True, blank=True)
#     sceleton = models.IntegerField(null=True, blank=True)
#     soil_ammonium = models.IntegerField(null=True, blank=True)
#     soil_nitrate = models.IntegerField(null=True, blank=True)
#     c_n = models.IntegerField(null=True, blank=True)
#     initial_soil_moisture = models.IntegerField(null=True, blank=True)
#     layer_description = models.CharField(max_length=56, null=True, blank=True)
#     is_in_groundwater = models.IntegerField(null=True, blank=True)
#     is_impenetrable = models.IntegerField(null=True, blank=True)
    
#     def __str__(self):
#         return 'soil_profile_all' + self.polygon_id + self.profile_id_in_polygon
    




# class BuekBulkDensityClassToRawDensity(models.Model):
#     bulk_density_class = models.AutoField(primary_key=True, blank=True, null=True)
#     raw_density_g_per_cm3 = models.FloatField(blank=True, null=True)

#     class Meta:
        
#         db_table = 'bulk_density_class_to_raw_density'


# class BuekHumusClassToCorg(models.Model):
#     humus_class = models.AutoField(primary_key=True, blank=True, null=True)
#     corg = models.FloatField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)

#     class Meta:
        
#         db_table = 'humus_class_to_corg'


# class BuekKa5SoiltypeToSandAndClay(models.Model):
#     ka5_soiltype = models.TextField(primary_key=True, blank=True, null=True)
#     sand = models.FloatField(blank=True, null=True)
#     clay = models.FloatField(blank=True, null=True)

#     class Meta:
        
#         db_table = 'ka5_soiltype_to_sand_and_clay'


# class BuekPhClassToPhValue(models.Model):
#     ph_class = models.TextField(primary_key=True, blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     ph_value_from = models.FloatField(blank=True, null=True)
#     ph_value_to = models.FloatField(blank=True, null=True)

#     class Meta:
        
#         db_table = 'ph_class_to_ph_value'


# class BuekTblblattlegendeneinheit(models.Model):
#     tkle_nr = models.AutoField(db_column='TKLE_NR', primary_key=True, blank=True, null=True)  # Field name made lowercase.
#     tk = models.TextField(db_column='TK', blank=True, null=True)  # Field name made lowercase.
#     le_nr = models.IntegerField(db_column='LE_NR', blank=True, null=True)  # Field name made lowercase.
#     le_txt = models.TextField(db_column='LE_TXT', blank=True, null=True)  # Field name made lowercase.
#     le_kurz = models.TextField(db_column='LE_KURZ', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
        
#         db_table = 'tblBlattlegendeneinheit'


# class BuekHorizon(models.Model):
#     gen_id = models.AutoField(db_column='GEN_ID', primary_key=True, blank=True, null=True)  # Field name made lowercase. The composite primary key (GEN_ID, BF_ID, HOR_NR) found, that is not supported. The first column is selected.
#     bf_id = models.IntegerField(db_column='BF_ID', blank=True, null=True)  # Field name made lowercase.
#     hor_nr = models.IntegerField(db_column='HOR_NR', blank=True, null=True)  # Field name made lowercase.
#     otief = models.FloatField(db_column='OTIEF', blank=True, null=True)  # Field name made lowercase.
#     utief = models.FloatField(db_column='UTIEF', blank=True, null=True)  # Field name made lowercase.
#     sw_horiz = models.TextField(db_column='SW_HORIZ', blank=True, null=True)  # Field name made lowercase.
#     horiz = models.TextField(db_column='HORIZ', blank=True, null=True)  # Field name made lowercase.
#     boart = models.TextField(db_column='BOART', blank=True, null=True)  # Field name made lowercase.
#     grobbod_f = models.TextField(db_column='GROBBOD_F', blank=True, null=True)  # Field name made lowercase.
#     grobbod_k = models.IntegerField(db_column='GROBBOD_K', blank=True, null=True)  # Field name made lowercase.
#     humus = models.TextField(db_column='HUMUS', blank=True, null=True)  # Field name made lowercase.
#     kalk = models.TextField(db_column='KALK', blank=True, null=True)  # Field name made lowercase.
#     kohle = models.TextField(db_column='KOHLE', blank=True, null=True)  # Field name made lowercase.
#     substrart = models.TextField(db_column='SUBSTRART', blank=True, null=True)  # Field name made lowercase.
#     ph = models.TextField(db_column='PH', blank=True, null=True)  # Field name made lowercase.
#     ld = models.TextField(db_column='LD', blank=True, null=True)  # Field name made lowercase.
#     gefuege = models.TextField(db_column='GEFUEGE', blank=True, null=True)  # Field name made lowercase.
#     sv = models.TextField(db_column='SV', blank=True, null=True)  # Field name made lowercase.
#     strat = models.TextField(db_column='STRAT', blank=True, null=True)  # Field name made lowercase.
#     strat_juengst_praeg = models.TextField(db_column='STRAT_JUENGST_PRAEG', blank=True, null=True)  # Field name made lowercase.
#     strat_ursp = models.TextField(db_column='STRAT_URSP', blank=True, null=True)  # Field name made lowercase.
#     geogen = models.TextField(db_column='GEOGEN', blank=True, null=True)  # Field name made lowercase.
#     herk = models.TextField(db_column='HERK', blank=True, null=True)  # Field name made lowercase.
#     lage = models.TextField(db_column='LAGE', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
        
#         db_table = 'tblHorizonte'


# class BuekProfile(models.Model):
#     projekt = models.TextField(db_column='Projekt', blank=True, null=True)  # Field name made lowercase.
#     gen_id = models.AutoField(db_column='GEN_ID', primary_key=True, blank=True, null=True)  # Field name made lowercase. The composite primary key (GEN_ID, BOF_NR) found, that is not supported. The first column is selected.
#     bf_id = models.IntegerField(db_column='BF_ID', blank=True, null=True)  # Field name made lowercase.
#     bof_nr = models.IntegerField(db_column='BOF_NR', blank=True, null=True)  # Field name made lowercase.
#     status = models.TextField(db_column='STATUS', blank=True, null=True)  # Field name made lowercase.
#     bodtyp = models.TextField(db_column='BODTYP', blank=True, null=True)  # Field name made lowercase.
#     bodsysteinh = models.TextField(db_column='BODSYSTEINH', blank=True, null=True)  # Field name made lowercase.
#     substrsubtyp = models.TextField(db_column='SUBSTRSUBTYP', blank=True, null=True)  # Field name made lowercase.
#     neigdom = models.TextField(db_column='NeigDom', blank=True, null=True)  # Field name made lowercase.
#     neigmax = models.TextField(db_column='NEIGMax', blank=True, null=True)  # Field name made lowercase.
#     neigmin = models.TextField(db_column='NEIGMin', blank=True, null=True)  # Field name made lowercase.
#     expos = models.TextField(db_column='EXPOS', blank=True, null=True)  # Field name made lowercase.
#     rlform = models.TextField(db_column='RLFORM', blank=True, null=True)  # Field name made lowercase.
#     kultur = models.TextField(db_column='KULTUR', blank=True, null=True)  # Field name made lowercase.
#     erosi = models.TextField(db_column='EROSI', blank=True, null=True)  # Field name made lowercase.
#     egrad = models.TextField(db_column='EGRAD', blank=True, null=True)  # Field name made lowercase.
#     huform = models.TextField(db_column='HUFORM', blank=True, null=True)  # Field name made lowercase.
#     gws = models.TextField(db_column='GWS', blank=True, null=True)  # Field name made lowercase.
#     spezgw = models.TextField(db_column='SPEZGW', blank=True, null=True)  # Field name made lowercase.
#     vngrad = models.TextField(db_column='VNGRAD', blank=True, null=True)  # Field name made lowercase.
#     oekfeu = models.TextField(db_column='OEKFEU', blank=True, null=True)  # Field name made lowercase.
#     mhgw = models.TextField(db_column='MHGW', blank=True, null=True)  # Field name made lowercase.
#     mgw = models.TextField(db_column='MGW', blank=True, null=True)  # Field name made lowercase.
#     mngw = models.TextField(db_column='MNGW', blank=True, null=True)  # Field name made lowercase.
#     flant_spanne = models.TextField(db_column='FLANT_SPANNE', blank=True, null=True)  # Field name made lowercase.
#     flant_mittelw = models.IntegerField(db_column='FLANT_MITTELW', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
        
#         db_table = 'tblProfile'


# class TblzuordnunggleBle(models.Model):
#     tkle_nr = models.AutoField(db_column='TKLE_NR', primary_key=True, blank=True, null=True)  # Field name made lowercase.
#     gen_id = models.IntegerField(db_column='GEN_ID', blank=True, null=True)  # Field name made lowercase.
#     tk = models.TextField(db_column='TK', blank=True, null=True)  # Field name made lowercase.
#     le_nr = models.IntegerField(db_column='LE_NR', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
        
#         db_table = 'tblZuordnungGLE_BLE'
