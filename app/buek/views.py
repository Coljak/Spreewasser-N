from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import Point, Polygon, GEOSGeometry

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SoilProfileSerializer, MapSoilCLCSerializer
from datetime import datetime
from . import models
import json



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
    polygon_id = models.Buek200.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon_id) == 0:
        return {'error': 'No data found for the given coordinates'}
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon_id = polygon_id[0].polygon_id

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
    polygon = models.MapSoilCLC.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon) == 0:
        return Response(
            {'error': 'No data found for the given coordinates'},
            status=status.HTTP_404_NOT_FOUND
        )
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon = polygon[0]
    serializer = MapSoilCLCSerializer(polygon, many=False)

    return Response(serializer.data)


def get_soil_data_for_modal(soil_profile):
    """
    This return the soil data as a dictionary with information on the profile, as well as its horizons.
    Since there are many profiles in the buek that need to be adjusted, both datasets - the corrected as well as the original -
    are returned in the dictionary.
    
    :param soil_profile: buek_models.SoilProfile object
    """
    serializer = SoilProfileSerializer(soil_profile, many=False)
    soil_data = serializer.data
    corrected_horizons = soil_profile.get_monica_horizons_json()
    original = soil_profile.get_horizons_json()
    # if corrected_horizons == original:
    #     soil_data["SoilProfileParameters"] = original
    # else:
    soil_data["SoilProfileParameters"], _ = corrected_horizons
    soil_data["OriginalSoilProfileParameters"] = original

    def join_list_values(horizon):
        for key, value in horizon.items():
            if isinstance(value, list):
                value = [str(v).replace('kg m-3', ' kg/m³') for v in value]
                horizon[key] = ''.join(map(str, value))
        return horizon
    
    for hor in soil_data['OriginalSoilProfileParameters']:
        hor = join_list_values(hor)
        # for key, value in hor.items():
        #     if isinstance(value, list):
        #         value = [str(v).replace('kg m-3', ' kg/m³') for v in value]
        #         hor[key] = ''.join(map(str, value))

    for hor in soil_data['SoilProfileParameters']:
        hor = join_list_values(hor)

    return soil_data


def get_recommended_soil_profile(profile_type, lat, lon):
    """
    This produces soil profiles at the given longitude and latitude. 
    The profile_type general provides a soilprofile according to the CLC landuse.
    The profile_types agriculture and forest produce profiles agricultural and forest 
    profiles where such a profile exists in the buek and where the landuse is agricultural or forests.
    In all other cases, the profile is according to the landuse.  
    """ 
    lat = float(lat)
    lon = float(lon)

    polygon = models.MapSoilCLC.objects.filter(geom__contains=Point(lon, lat))[0]
    soil_data = {}
    # TODO: Deal with error messages (_)
    if profile_type == 'general':
        soil_data = get_soil_data_for_modal(polygon.soilprofile)

    elif profile_type == 'agriculture':
        soil_data = get_soil_data_for_modal(polygon.bias_21_soilprofile)
    elif profile_type == 'grassland':
        soil_data = get_soil_data_for_modal(polygon.bias_23_soilprofile)
    elif profile_type == 'forest':
        soil_data = get_soil_data_for_modal(polygon.bias_31_soilprofile)
    else:
        return {'error': profile_type + ' is not a valid profile type. Please use one of the following: general, agriculture, grassland, forest'}
    print('get_recommended_soil_profile', soil_data)
    return soil_data

@api_view(['GET'])
def get_recommended_soil_profile_from_point(request, profile_type, lat, lon):
    """
    
    """ 
    soil_data = get_recommended_soil_profile(profile_type, lat, lon)

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
    polygon_id = models.Buek200.objects.filter(geom__contains=Point(lon, lat))
    if len (polygon_id) == 0:
        return {'error': 'No data found for the given coordinates'}
    else:
        # the case where the coordinates are on the borders of more than one polygon returns only the first polygon's id 
        polygon_id = polygon_id[0].polygon_id
    
    soil_data = models.SoilProfile.objects.filter(polygon_id=polygon_id)
    # soil_serializer = SoilProfileSerializer(soil_data, many=True)
    response_dict = [soil.get_horizons_json() for soil in soil_data ]

    return Response(response_dict)





