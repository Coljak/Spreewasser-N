# from django.core.management.base import BaseCommand
# from swn.models import BuekCLCRaster
from django.contrib.gis.gdal import DataSource, GDALRaster, SpatialReference


from osgeo import gdal, osr
from django.core.management.base import BaseCommand
from swn.models import BuekCLCRaster

class Command(BaseCommand):
    help = 'Load and modify raster data into DB'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the raster file')
        parser.add_argument('burn_in_key', type=str, help='Parameter key of the raster values') 
        parser.add_argument('burn_in_description', type=str, help='Parameter description of the raster values')
        parser.add_argument('name', type=str, help='Name of the raster')
        parser.add_argument('grid_size_m', type=int, help='Approximate grid size of the raster in meters')
        parser.add_argument('--srid', type=int, default=4326, help='SRID of the raster')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        burn_in_description = kwargs['burn_in_description']
        name = kwargs['name']
        grid_size_m = kwargs['grid_size_m']
        srid = kwargs['srid']
        
        # Open the raster dataset in write mode
        raster = GDALRaster(file_path, 'w')
    
        
        # Save to the database using Django ORM
        raster_instance = BuekCLCRaster(
            name=name, 
            raster_data=raster, 
            burn_in_description=burn_in_description, 
            grid_size_m=grid_size_m
        )
        raster_instance.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded and modified raster data'))
