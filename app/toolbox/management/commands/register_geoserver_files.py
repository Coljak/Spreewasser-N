"""
With this command, monthly and yearly averages are produced or updated from the data saved in TimeseriesDailyWaterlevel."""
from django.core.management.base import BaseCommand
from django.db.models import Avg
from django.db.models.functions import TruncMonth, TruncYear
from toolbox import models
from pathlib import Path
from geo.Geoserver import Geoserver
import os


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


TOOLBOX_VECTOR_TABLES = ['toolbox_ezg25']


geo = Geoserver(settings.GEOSERVER_URL, username=settings.GEOSERVER_USER, password=settings.GEOSERVER_PASS)




def publish_all(workspace='spreewassern_raster'):
    for item in TOOLBOX_RASTER_FILES:
        
        geo.create_coveragestore(layer_name=item['name'], path=f'/app/raster_data/{item["name"]}.tif', workspace=workspace)
        
        geo.upload_style(path=f'/app/raster_data/{item["style"]}.sld', workspace=workspace)
        if item['style'] is not None:  
            geo.publish_style(layer_name=item['name'], style_name=item['style'], workspace=workspace)



def register_vector_files(workspace='spreewassern_vector', store_name='swn_featurestore'):
    geo.create_featurestore(
        store_name='swn_featurestore',
        workspace='spreewassern_vector',
        db=os.environ["DB_NAME"],
        host=os.environ["DB_HOST"],  
        port='5432',
        pg_user=os.environ["DB_USER"],
        pg_password=os.environ["DB_PASS"],
        schema='public'
    )
    for item in TOOLBOX_VECTOR_TABLES:
        geo.publish_featurestore(workspace=workspace, store_name=store_name, pg_table=item)

def register_style_files(workspace='spreewassern_raster'):
    sld_dir = '/app/raster_data'
    for filename in os.listdir(sld_dir):
        if filename.endswith(".sld"):
            filepath = os.path.join(sld_dir, filename)
            geo.upload_style(path=filepath, workspace=workspace)


class Command(BaseCommand):
    help = 'Set up the geoserver with workspaces, styles and files'

    geo.create_workspace(workspace='spreewassern_raster')
    geo.create_workspace(workspace='spreewassern_vector')
    register_style_files()
    
    publish_all()
    