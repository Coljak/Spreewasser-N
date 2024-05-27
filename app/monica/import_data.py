from monica import models
from swn import models as swn_models
from django.contrib.gis.geos import Point
from monica.climate_data.lat_lon_mask import lat_lon_mask as mask
from datetime import datetime

"""
This function inserts the centroids of the DWD raster grid cells as points into the database.
It fills the db-table DWDGridToPointIndices from the lat_lon_mask file.
"""
def create_multipoint_from_dwd_grid():
    start = datetime.now()
    for lat in mask['lat']:
        for lon in mask['lon']:
            models.DWDGridToPointIndices.objects.create(
                point=Point(lon, lat, srid=4326),
                lat=lat,
                lon=lon,
                lat_idx=mask['lat'].index(lat),
                lon_idx=mask['lon'].index(lon),
                is_valid=mask['mask'][mask['lat'].index(lat)][mask['lon'].index(lon)]
            )
    
    
        