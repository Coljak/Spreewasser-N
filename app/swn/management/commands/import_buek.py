from django.contrib.gis.gdal import DataSource

"""
This script can be run to import the buek data into the database.
"""
path_to_buek = input('Please insert the path to buek200_buffered_3m.shp')
ds = DataSource(path_to_buek)