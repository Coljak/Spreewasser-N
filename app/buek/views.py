from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point, Polygon, GEOSGeometry

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SoilProfileSerializer, MapSoilCLCSerializer
from datetime import datetime
from .models import *



def test_split(request):
    return render(request, 'shared/three_split.html')

@api_view(['GET'])
def api_schema(request):
    # this is a list of API routes in the buek app
    routes = [
        {'GET': '/buek/api/soil_data/<lat>/<lon>/', 'description': 'Get the soil data for a given latitude and longitude'},
        {'GET': '/buek/api/soil_profile/agriculture/<lat>/<lon>/', 'description': 'Get the soil data for a given latitude and longitude. If available, an agricultural soil profile is prvided.'},
        {'GET': '/buek/api/soil_profile/forest/<lat>/<lon>/', 'description': 'Get the soil data for a given latitude and longitude. If available, a forest soil profile is prvided.'},
        {'GET': '/buek/api/soil_profile/grassland/<lat>/<lon>/', 'description': 'Get the soil data for a given latitude and longitude. If available, a grassland soil profile is prvided.'},
        {'GET': '/buek/api/soil_profile/grassland/<lat>/<lon>/', 'description': 'Get the soil data for a given latitude and longitude. If available, a grassland soil profile is prvided.'},
        {'GET': '/buek/api/original_buek200/<lat>/<lon>/', 'description': 'Get the original Buek200 soil profiles for a given latitude and longitude.'},
    ]
    return Response(routes)


def get_buek_polygon_id_from_point_buek200(lat, lon):
    """
    This function retrieves the original Buek Polygon by polygon_id (TKLE_NR).
    The Vectorfile used is the original Buek200 with no extra information
    """
    lat = float(lat)
    lon = float(lon)
    start = datetime.now()
    # Get the soil data from the BUEK200 database
    polygon_id = Buek200.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon_id) == 0:
        return {'error': 'No data found for the given coordinates'}
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon_id = polygon_id[0].polygon_id
    
    print('Time elapsed getting soil profile: ', datetime.now() - start)
    return polygon_id

@api_view(['GET'])
def get_buek_data_from_point(request, lat, lon):
    """
    This function returns all references to soilprofiles in one point.
    tkle_nr is the id of the polygon in the BUEK200 database,
    polygon_id id the id of the polygon used to provide the soil data in cases where either no data or no appropriate data is available in the Buek200,
    ....
    """ 
    lat = float(lat)
    lon = float(lon)
    start = datetime.now()
    # Get the soil data from the BUEK200 database
    polygon = MapSoilCLC.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon) == 0:
        return Response(
            {'error': 'No data found for the given coordinates'},
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon = polygon[0]
    print('Polygon:', polygon)
    serializer = MapSoilCLCSerializer(polygon, many=False)
    print('Time elapsed getting soil profile: ', datetime.now() - start)
    return Response(serializer.data)



def get_soil_profile(profile_type, lat, lon):
    """
    This function returns all references to soilprofiles in one point.
    tkle_nr is the id of the polygon in the BUEK200 database,
    polygon_id id the id of the polygon used to provide the soil data in cases where either no data or no appropriate data is available in the Buek200,
    ....
    """ 
    lat = float(lat)
    lon = float(lon)

    polygon = MapSoilCLC.objects.filter(geom__contains=Point(lon, lat))[0]
    soil_data = {}
    # TODO: Deal with error messages (_)
    if profile_type == 'general':
        serializer = SoilProfileSerializer(polygon.soilprofile, many=False)
        soil_data = serializer.data
        soil_data["SoilProfileParameters"], _ = polygon.soilprofile.get_monica_horizons_json()
        soil_data["OriginalSoilProfileParameters"] = polygon.soilprofile.get_horizons_json()
        
    elif profile_type == 'agriculture':
        serializer = SoilProfileSerializer(polygon.bias_21_soilprofile, many=False)
        soil_data = serializer.data
        soil_data["SoilProfileParameters"], _ = polygon.bias_21_soilprofile.get_monica_horizons_json()
        soil_data["OriginalSoilProfileParameters"] = polygon.bias_21_soilprofile.get_horizons_json()
    elif profile_type == 'grassland':
        serializer = SoilProfileSerializer(polygon.bias_23_soilprofile, many=False)
        soil_data = serializer.data
        soil_data["SoilProfileParameters"], _ = polygon.bias_23_soilprofile.get_monica_horizons_json()
        soil_data["OriginalSoilProfileParameters"] = polygon.bias_23_soilprofile.get_horizons_json()
    elif profile_type == 'forest':
        serializer = SoilProfileSerializer(polygon.bias_31_soilprofile, many=False)
        soil_data = serializer.data
        soil_data["SoilProfileParameters"], _ = polygon.bias_31_soilprofile.get_monica_horizons_json()
        soil_data["OriginalSoilProfileParameters"] = polygon.bias_31_soilprofile.get_horizons_json()
    else:
        return {'error': profile_type + ' is not a valid profile type. Please use one of the following: general, agriculture, grassland, forest'}

    return soil_data

@api_view(['GET'])
def get_soil_profile_from_point(request, profile_type, lat, lon):
    """
    This function returns all references to soilprofiles in one point.
    tkle_nr is the id of the polygon in the BUEK200 database,
    polygon_id id the id of the polygon used to provide the soil data in cases where either no data or no appropriate data is available in the Buek200,
    ....
    """ 
    soil_data = get_soil_profile(profile_type, lat, lon)

    return Response(soil_data)



@api_view(['GET'])
def get_profiles_from_point_buek200(request, lat, lon):
    """
    This function retrieves the original Buek Soil Profiles by polygon_id (TKLE_NR).
    The Vectorfile used is the original Buek200 with no extra information. There are blankareas.
    """
    lat = float(lat)
    lon = float(lon)
    start = datetime.now()
    # Get the soil data from the BUEK200 database
    polygon_id = Buek200.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon_id) == 0:
        return {'error': 'No data found for the given coordinates'}
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon_id = polygon_id[0].polygon_id
    
    soil_data = SoilProfile.objects.filter(polygon_id=polygon_id)
    # soil_serializer = SoilProfileSerializer(soil_data, many=True)
    response_dict = [soil.get_horizons_json() for soil in soil_data ]
    
    print('Time elapsed getting soil profile: ', datetime.now() - start)
    return Response(response_dict)


def get_soil_data_by_polygon_id(polygon_id):
    soil_data = SoilProfileHorizon.objects.select_related('soilprofile').filter(soilprofile__polygon_id=polygon_id).order_by('soilprofile__area_percentage', 'obergrenze_m')

    return soil_data


