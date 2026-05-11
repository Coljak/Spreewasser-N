from django.db.models import Min, Max
import math
from django.conf import settings
from geo.Geoserver import Geoserver


def get_bounds(qs, field):
    agg = qs.aggregate(min_val=Min(field), max_val=Max(field))
    if agg['min_val'] is None or agg['max_val'] is None:
        return [0, 1]
    return [math.floor(agg['min_val']), math.ceil(agg['max_val'])]



def publish_raster_on_geoserver(
        layer_name, 
        path=settings.TOOLBOX_RASTER_DATA_DIR, 
        workspace='spreewassern_raster', 
        style_name="style_raster_percent_sieker_2"
        ):
    """
    Publishes a GeoTIFF to GeoServer as a coverage store and attaches an existing style.
    """

    geo = Geoserver(
        settings.GEOSERVER_URL,
        username=settings.GEOSERVER_USER,
        password=settings.GEOSERVER_PASS
    )

    geo.create_coveragestore(layer_name=layer_name, path=f'{path}/{layer_name}.tif', workspace=workspace)
    geo.publish_style(layer_name=layer_name, style_name=style_name, workspace=workspace)