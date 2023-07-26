"""This script loads the NUTS shapefiles into the database"""

from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import *   
from django.contrib.gis.gdal import DataSource

# To run this file adjust the mapping and do python manage.py shell, from swn import load_geo, load_geo.run()
# https://docs.djangoproject.com/en/4.2/ref/contrib/gis/tutorial/

shp_path = Path(__file__).resolve().parent.parent / "geodata" / "nuts5000_4326" /"nuts5000_n3_4326.shp"



nuts_mapping = {
    "objid": "OBJID",
    "beginn": "BEGINN",
    "gf": "GF",
    "nuts_level": "NUTS_LEVEL",
    "nuts_code": "NUTS_CODE",
    "nuts_name": "NUTS_NAME",
    "geom": "POLYGON",
}


def run(verbose=True):
    lm = LayerMapping(NUTS5000_N3, shp_path, nuts_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)