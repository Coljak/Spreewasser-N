"""
Django admin customization.
"""

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# this is best practice to integrate translation
from django.utils.translation import gettext_lazy as _

from .models import User, ProjectRegion
# from Waterconsumption Tutorial
from django.contrib.gis.geos import Point, Polygon, MultiPoint, MultiPolygon
from datetime import datetime
import pandas as pd
from pandas import ExcelWriter, ExcelFile


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for the user."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ( # get_lazy is called
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',), # custom CSS-class
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

class ProjectRegionAdmin(LeafletGeoAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(ProjectRegion, LeafletGeoAdmin)