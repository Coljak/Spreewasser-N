from django.contrib.gis.gdal import DataSource
from .models import DigitalElevationModel10

def import_geotiff(filepath):
    ds = DataSource(filepath)
    layer = ds[0]
    for feature in layer:
        rast = feature.geom  # Rasterdaten
        extent = rast.extent  # Polygon-Grenzen
        dem = DigitalElevationModel10(rast=rast.wkb, extent=extent)
        dem.save()