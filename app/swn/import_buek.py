""" This script is only for loading the Buek200 Vektorfile into the swn database."""

from django.contrib.gis.utils import LayerMapping
from models import Buek

# Auto-generated `LayerMapping` dictionary for Buek model
buek_mapping = {
    
    'polygon_id': 'TKLE_NR',
    'bgl': 'BGL',
    'symbol': 'Symbol',
    'legende': 'Legende',
    'hinweis': 'Hinweis',
    'shape_area': 'Shape_Area',
    'shape_leng': 'Shape_Leng',
    'geom': 'MULTIPOLYGON',
}

shapefile_path = '././geodata/buek_vektor/buek200_buffered_3m_4326.shp'

layer_mapping = LayerMapping(Buek, shapefile_path, buek_mapping, transform=False, encoding='iso-8859-1')
layer_mapping.save(strict=True, verbose=True)