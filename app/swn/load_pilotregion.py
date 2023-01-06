""" this file is run in order to imort data into the GeoDB
    https://docs.djangoproject.com/en/4.0/ref/contrib/gis/layermapping/

"""
#TODO THIS IS NOT WORKING!!!!
from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from models import PilotRegion


BASE_PATH = Path(__file__).resolve().parent
GEODATA_PATH = Path.joinpath(BASE_PATH, 'Geodata')

pilotregion_mapping = {
    'kennzahl': 'KENNZAHL',
    'gewaesser': 'GEWAESSER',
    'gew_alias': 'GEW_ALIAS',
    'gew_kennz': 'GEW_KENNZ',
    'beschr_von': 'BESCHR_VON',
    'beschr_bis': 'BESCHR_BIS',
    'lage': 'LAGE',
    'land': 'LAND',
    'ordnung': 'ORDNUNG',
    'fl_art': 'FL_ART',
    'wrrl_kr': 'WRRL_KR',
    'area_qkm': 'AREA_QKM',
    'area_ha': 'AREA_HA',
    'ezg_id': 'EZG_ID',
    'bemerkung': 'BEMERKUNG',
    'wrrl_fge': 'WRRL_FGE',
    'wrrl_bg': 'WRRL_BG',
    'geom': 'MULTIPOLYGON',
}



shp = Path.joinpath(GEODATA_PATH, 'Pilotregion_SpreeWasserN.shp')

def run(verbose=True):
    print('Country: ', PilotRegion, shp)
    lm = LayerMapping(PilotRegion, shp, pilotregion_mapping)
    lm.save(verbose=True)

if __name__ == "__main__":
    run()