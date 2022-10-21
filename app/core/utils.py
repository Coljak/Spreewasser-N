from django.contrib.gis.geoip2 import GeoIP2


# helper function to get user's ip location
def get_geolocation(ip):
    g = GeoIP2()

    lat, lon = g.lat_lon(ip)

    return lat, lon