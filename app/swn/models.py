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
    field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, null=True)
    comment = models.TextField(null=True, blank=True)
    irrigation_input = models.JSONField(null=True, blank=True)
    irrigation_output = models.JSONField(null=True, blank=True)
    calculation = models.JSONField(null=True, blank=True)
    date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name

