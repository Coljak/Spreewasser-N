from django.contrib.gis.gdal import DataSource
import swn.data
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
import geopandas as gpd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from swn.models import BaseRasterData, UserField


user_field = UserField.objects.get(pk=287)

# Dataframe to 100 x 100 raster

df = gpd.read_file('././app/geodata/buek_vektor/buek200_buffered_3m.shp')

df = df.to_crs(epsg=4326)

shape = 100, 100
transform = rasterio.transform.from_bounds(*df['geometry'].total_bounds, *shape)
rasterize_buek = rasterize(
    [(shape, 1) for shape in df['geometry']],
    out_shape=shape,
    transform=transform,
    fill=0,
    all_touched=True,
    dtype=rasterio.uint8)

with rasterio.open(
    '././app/geodata/buek_vektor/buek200_4326.tif', 'w',
    driver='GTiff',
    dtype=rasterio.uint8,
    count=1,
    width=shape[0],
    height=shape[1],
    transform=transform
) as dst:
    dst.write(rasterize_buek, indexes=1)