"""
Database models.
"""

from email.policy import default
from statistics import mode

from django.contrib.gis.db import models
from djgeojson.fields import PointField, PolygonField, MultiLineStringField, MultiPointField, MultiPolygonField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import datetime
import os

class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class WinterSummerCrop(models.Model):
    name = models.CharField(max_length=30)
    
class Crop(models.Model):
    name = models.CharField(max_length=64)
    winter_summer_crop = models.ForeignKey(WinterSummerCrop, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class ProjectRegion(models.Model):
    name = models.CharField(max_length=50)
    geom = models.MultiPolygonField(null=True)

    def __str__(self):
        return self.name

class UserField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    geom = PolygonField(null=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# class UserIrrigation(models.Model):
#     date = models.DateField()
#     amount = models.PositiveIntegerField()

class UserProject(models.Model):    
    name = models.CharField(max_length=255)
    field = models.ForeignKey(UserField, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.DO_NOTHING, null=True)
    comment = models.TextField(null=True, blank=True)
    irrigation_input = models.JSONField(null=True, blank=True)
    irrigation_output = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.name
