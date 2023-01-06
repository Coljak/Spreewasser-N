# NOT SURE IF WORKING!!!!
import json
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon

from models import ProjectRegion

with open('data/pilotregion_4326.geojson') as f:
    data = json.load(f)

for ft in data['features']:
    geom_str = json.dumps(ft['geometry'])
    geom = GEOSGeometry(geom_str)
    try:
        if isinstance(geom, MultiPolygon):
            continue
        elif isinstance(geom, Polygon):
            geom = MultiPolygon([geom])
        else:
            raise TypeError(
                '{} not acceptable for this model'.format(geom.geom_type)
            )
        
        item = ProjectRegion(geom=geom)
        item.save()
        
    except TypeError as e:
        print(e)
