"""
With this command, monthly and yearly averages are produced or updated from the data saved in TimeseriesDailyWaterlevel."""
from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.db.models.functions import TruncMonth, TruncYear
from toolbox import models


TOOLBOX_RASTER_FILES = [
    {'name': 'no_injection_area_mask_v2', 'workspace': 'spreewassern_raster', 'style': None,},
    {'name': 'land_use', 'workspace': 'spreewassern_raster', 'style': 'style_land_use'},
    {'name': 'aquifer_classified_v1', 'workspace': 'spreewassern_raster', 'style': 'style_aquifer_classified'},
    {'name': 'depth_to_gw_classified_v1', 'workspace': 'spreewassern_raster', 'style': 'style_depth_to_gw_classified'},
    {'name': 'distance_to_source_water_v1', 'workspace': 'spreewassern_raster', 'style': 'style_distance_to_source_water'},
    {'name': 'distance_to_extraction_wells_v1', 'workspace': 'spreewassern_raster', 'style': 'style_distance_to_extraction_wells'},
    {'name': 'hydraulic_conductivity_classified_v1', 'workspace': 'spreewassern_raster', 'style': 'style_hydraulic_conductivity_classified'},
    #sieker
    {'name': 'Umsetzbarkeit_Hangneigung', 'workspace': 'spreewassern_raster', 'style': None},
    {'name': 'Entwaesserungswahrscheinlichkeit_9Parameter_v2', 'workspace': 'spreewassern_raster', 'style': 'style_raster_percent_sieker_2'}
    ]


geo = Geoserver(settings.GEOSERVER_URL, username=settings.GEOSERVER_USER, password=settings.GEOSERVER_PASS)




def publish_all(workspace='spreewassern_raster'):
    for item in TOOLBOX_RASTER_FILES:
        
        geo.create_coveragestore(layer_name=item['name'], path=f'/app/raster_data/{item["name"]}.tif', workspace=workspace)
        if item['style'] is not None:
            geo.upload_style(path=f'/app/raster_data/{item["style"]}.sld', workspace=workspace)
            geo.publish_style(layer_name=item['name'], style_name=item['style'], workspace=workspace)


class Command(BaseCommand):
    help = 'Set up the geoserver with workspaces, styles and files'

    geo.create_workspace(workspace='spreewassern_raster')
    publish_all()
    