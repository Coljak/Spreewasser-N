"""
Database models.
"""

from email.policy import default
from statistics import mode

from django.contrib.gis.db import models
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
    geom = models.MultiPolygonField()

    def __str__(self):
        return self.name

class UserField(models.Model):
    name = models.CharField(max_length=255)
    geom = models.MultiPolygonField()
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name, self.user.name

class UserIrrigation(models.Model):
    date = models.DateField()
    amount = models.PositiveIntegerField()

class UserProject(models.Model):
    # TODO get User
    # user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    field = models.ForeignKey(UserField, on_delete=models.DO_NOTHING)
    comment = models.TextField()
    irrigation = models.ForeignKey(UserIrrigation, on_delete=models.SET_NULL, null=True)
    geom = models.PolygonField(null=True)
    def __str__(self):
        return self.name, self.field.name
