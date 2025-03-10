"""
Django admin customization.
"""

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin, ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# this is best practice to integrate translation
from django.utils.translation import gettext_lazy as _

from .models import *
from django.contrib.gis.geos import Point, Polygon, MultiPoint, MultiPolygon
from datetime import datetime
import pandas as pd
from pandas import ExcelWriter, ExcelFile



class UserAdmin(BaseUserAdmin):
    """Define the admin pages for the user."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        # None is the title
        (None, {'fields': ('email', 'password')}),
        (
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
class UserFieldAdmin(LeafletGeoAdmin):
    list_display = ('id', 'user', 'name')

admin.site.register(ProjectRegion, LeafletGeoAdmin)

admin.site.register(UserField, UserFieldAdmin)
admin.site.register(SwnProject, ModelAdmin)
admin.site.register(NUTS5000_N1, LeafletGeoAdmin)
admin.site.register(NUTS5000_N2, LeafletGeoAdmin)
admin.site.register(NUTS5000_N3, LeafletGeoAdmin)
# admin.site.register(UserCalculation)
