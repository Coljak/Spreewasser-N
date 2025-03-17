from django.shortcuts import render
from . import models
from swn import models as swn_models
from swn import forms as swn_forms

from . import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db.models import F, Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models import PointField
from django.db import connection
# Create your views here.

def three_split(request):
    user_fields = models.UserField.objects.filter(user=request.user)
    outline_injection = json.loads(GEOSGeometry(models.OutlineInjection.objects.all()[0].geom).geojson)
    outline_infiltration = json.loads(GEOSGeometry(models.OutlineInfiltration.objects.all()[0].geom).geojson)
    outline_surface_water = json.loads(GEOSGeometry(models.OutlineSurfaceWater.objects.all()[0].geom).geojson)
    outline_geste = json.loads(GEOSGeometry(models.OutlineGeste.objects.all()[0].geom).geojson)

    projectregion = swn_models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    pr_feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }
    
    # NUTS Region selector
    state_county_district_form = swn_forms.PolygonSelectionForm()


    data = {
        'sidebar_header': 'Toolbox',
        'user_projects': user_fields,
        # 'toolbox_form': toolbox_form,
        'state_county_district_form': state_county_district_form,
        'outline_injection': outline_injection,
        'outline_infiltration': outline_infiltration,
        'outline_surface_water': outline_surface_water,
        'outline_geste': outline_geste,
        'project_region': pr_feature,
    }

    return render(request, 'toolbox/toolbox_three_split.html', data)





@login_required
def toolbox_dashboard(request):
    user_projects = models.UserProject.objects.filter(user_project__user=request.user)
    toolbox_form = forms.UserProjectForm()

    overlay_lelow_groundwaters = models.BelowGroundWaters.objects.all()
    overlay_above_groundwaters = models.AboveGroundWaters.objects.all()

    outline_injection = json.loads(GEOSGeometry(models.OutlineInjection.objects.all()[0].geom).geojson)
    outline_infiltration = json.loads(GEOSGeometry(models.OutlineInfiltration.objects.all()[0].geom).geojson)
    outline_surface_water = json.loads(GEOSGeometry(models.OutlineSurfaceWater.objects.all()[0].geom).geojson)
    outline_geste = json.loads(GEOSGeometry(models.OutlineGeste.objects.all()[0].geom).geojson)

    projectregion = swn_models.ProjectRegion.objects.all()
    # geometry = GEOSGeometry(projectregion[0].geom)
    # geojson = json.loads(geometry.geojson)

    data = {
        'sidebar_header': 'Toolbox',
        'user_projects': user_projects,
        'toolbox_form': toolbox_form,
        'outline_injection': outline_injection,
        'outline_infiltration': outline_infiltration,
        'outline_surface_water': outline_surface_water,
        'outline_geste': outline_geste,
        'project_region': projectregion,
    }

    user_fields = models.UserField.objects.get(user=request.user)
   

    for user_field in user_fields:
        item = {
            'name': user_field.name,
            'user_name': user_field.user.name,
            'description': user_field.description,
        }
        user_projects.append(item)



    return JsonResponse(data)

@login_required
def load_user_fields(request):
    user_fields = models.UserField.objects.filter(user=request.user)
    return JsonResponse(list(user_fields.values()), safe=False)

def get_user_fields(request):
    if request.method == "GET":
        print("GET, headers:", request.headers)
        print("GET, body:", request.body)
        user_projects = models.UserProject.objects.filter(user_field__user=request.user)
        user_fields = models.UserField.objects.filter(user=request.user)

    return JsonResponse({'user_fields': list(user_fields.values('id', 'user', 'name', 'geom_json')), 'user_projects': list(user_projects.values())})

@login_required
def save_user_field(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        user_field = models.UserField.objects.create(body.get('name'), body.get('description'), body.get('geom'), request.user)
        
        user_fields = models.UserField.objects.filter(user=request.user)
        return JsonResponse(list(user_fields.values()), safe=False)
        return JsonResponse({'name': 'FIX THIS VIEW'}, safe=False)


def load_toolbox_sinks(request):
    # Retrieve all polygons from the database table
    toolbox_sinks = models.SinksWithLandUseAndSoilPropertiesAsPoints.objects.all()

    # Initialize an empty list to store GeoJSON features
    features = []
    start_time = datetime.now()
    # Loop through each polygon and convert it to GeoJSON format
    for toolbox_sink in toolbox_sinks:
        geometry = GEOSGeometry(toolbox_sink.geom)
        # print(geometry.geojson)
        geojson = json.loads(geometry.geojson)
       
        features.append(geojson)

    # Create a GeoJSON FeatureCollection containing all GeoJSON features
    feature_collection = {
        "type": "FeatureCollection",
        "features": features,
    }
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
    # Return the GeoJSON FeatureCollection as a JSON response
    return JsonResponse(feature_collection)


# def load_toolbox_sinks(request):
#     with open('toolbox/static/data/geo_json_1.geojson') as f:
#         data = json.load(f)
#         print("Data: ", data)
#     return JsonResponse(data)

def load_outline_injection(request):
    outline_injection = models.OutlineInjection.objects.all()
    geometry = GEOSGeometry(outline_injection[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Toolbox Injection',
            }
        }
    return JsonResponse(feature)

def load_outline_surface_water(request):
    outline_surface_water = models.OutlineSurfaceWater.objects.all()
    geometry = GEOSGeometry(outline_surface_water[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Toolbox Surface Water',
            }
        }
    return JsonResponse(feature)

def load_outline_infiltration(request):
    outline_infiltration = models.OutlineInfiltration.objects.all()
    geometry = GEOSGeometry(outline_infiltration[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Toolbox Infiltration',
            }
        }
    return JsonResponse(feature)

def load_outline_geste(request):
    outline_geste = models.OutlineInfiltration.objects.all()
    geometry = GEOSGeometry(outline_geste[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Toolbox Geste',
            }
        }
    return JsonResponse(feature)

def load_outline_water_retention(request):
    water_retention = models.Wasserrueckhaltepotentiale.objects.all()
    geometry = GEOSGeometry(water_retention[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Toolbox Water Retention',
            }
        }
    return JsonResponse(feature)

def toolbox_get_sinks_within(request, area_id):
    user_field = swn_models.UserField.objects.get(id=area_id)
    user_field_geom = GEOSGeometry(user_field.geom)
    sinks = models.SinksWithLandUseAndSoilPropertiesAsPoints.objects.filter(
        geom__within=user_field_geom
    )
    features = []
    # print(sinks)
    for sink in sinks:
        geometry = GEOSGeometry(sink.geom)
        
        geojson = json.loads(geometry.geojson)
        geojson['properties'] = {
            "Tiefe": sink.depth_sink,
            "Fläche": sink.area_sink,
            "Eignung": str(sink.index_sink * 100) + "%",
            "Eignung 2": str(sink.index_si_1 * 100) + "%",
            "Landnuntzung 1": sink.landuse_1,
            "Landnuntzung 2": sink.landuse_2,
            "Landnuntzung 3": sink.landuse_3,
            "Bodenindex": sink.index_soil ,
        }
        features.append(geojson)
    feature_collection = {
        "type": "FeatureCollection",
        "features": features,
        }
    
    # soils = models.SoilProperties4326.objects.objects.filter(
    #     geom__within=user_field_geom
    # )
    # index_soil = sinks.values_list('index_soil', flat=True).distinct()
    # Return the GeoJSON FeatureCollection as a JSON response
    return JsonResponse(feature_collection)

    

def toolbox_sinks_edit(request, id):
    #user project
    area_id = id
    user_field = swn_models.UserField.objects.get(id=id)
    user_field_geom = GEOSGeometry(user_field.geom)
    sinks = models.SinksWithLandUseAndSoilPropertiesAsPoints.objects.filter(
        geom__within=user_field_geom
    )
    toolbox_edit_data = {
        'name': user_field.name,
        'area_id': area_id
    }

    sinks_list = []
    for obj in sinks:
        dict = {}
        dict['type'] = 'Point'
        dict['geom'] = json.loads(obj.geom.geojson)['coordinates']
        dict['objectid'] = obj.objectid
        dict['depth_sink'] = obj.depth_sink
        dict['area_sink'] = obj.area_sink
        dict['index_soil'] = obj.index_soil
        # dict['index_sink'] = obj.index_sink
        # dict['index_si_1'] = obj.index_si_1
        dict['land_use_1'] = obj.landuse_1
        dict['land_use_2'] = obj.landuse_2
        sinks_list.append(dict)
        # print(obj.geom)
    
    sinks_list_json = json.dumps(sinks_list)
    toolbox_edit_data['sinks'] = sinks_list

    distinct_land_use_1 = sinks.values_list('landuse_1', flat=True).distinct()
    distinct_land_use_2 = sinks.values_list('landuse_2', flat=True).distinct()
    depths_sink = sinks.values_list('depth_sink', flat=True).distinct()
    # max_depth_sink = sinks.values_list('depth_sink', flat=True).max()
    areas_sink = sinks.values_list('area_sink', flat=True).distinct()
    depths_sink = list(depths_sink)
    rounded_depths_list = [round(value, 2) for value in depths_sink]
    rounded_depths_list = list(set(rounded_depths_list))
    rounded_depths_list.sort()
    areas_sink = list(areas_sink)
    areas_sink.sort()
    toolbox_edit_data['depths_sink'] = rounded_depths_list
    toolbox_edit_data['areas_sink'] = areas_sink
    # max_area_sink = sinks.values_list('area_sink', flat=True).max()
    toolbox_edit_data['distinct_land_use_1'] = distinct_land_use_1
    toolbox_edit_data['distinct_land_use_2'] = distinct_land_use_2
    # toolbox_edit_data['min_depth_sink'] = min_depth_sink
    # toolbox_edit_data['max_depth_sink'] = max_depth_sink
    # toolbox_edit_data['min_area_sink'] = min_area_sink
    # toolbox_edit_data['max_area_sink'] = max_area_sink
    # print(distinct_land_use_1)
    return render(request, 'toolbox/toolbox_project_edit.html', toolbox_edit_data)



def sinks_filter(request):
    form = forms.SinksFilterForm(request.GET or None)
    sinks_queryset = models.SinksWithLandUseAndSoilPropertiesAsPoints.objects.all()

    if form.is_valid():
        # Filter based on depth_sink range
        depth_sink_min = form.cleaned_data.get('depth_sink_min')
        depth_sink_max = form.cleaned_data.get('depth_sink_max')
        if depth_sink_min is not None:
            sinks_queryset = sinks_queryset.filter(depth_sink__gte=depth_sink_min)
        if depth_sink_max is not None:
            sinks_queryset = sinks_queryset.filter(depth_sink__lte=depth_sink_max)

        # Filter based on area_sink range
        area_sink_min = form.cleaned_data.get('area_sink_min')
        area_sink_max = form.cleaned_data.get('area_sink_max')
        if area_sink_min is not None:
            sinks_queryset = sinks_queryset.filter(area_sink__gte=area_sink_min)
        if area_sink_max is not None:
            sinks_queryset = sinks_queryset.filter(area_sink__lte=area_sink_max)

        # Filter based on calculated volume (area_sink * depth_sink)
        volume_min = form.cleaned_data.get('volume_min')
        volume_max = form.cleaned_data.get('volume_max')
        if volume_min is not None:
            sinks_queryset = sinks_queryset.annotate(
                volume=F('area_sink') * F('depth_sink')
            ).filter(volume__gte=volume_min)

        if volume_max is not None:
            sinks_queryset = sinks_queryset.annotate(
                volume=F('area_sink') * F('depth_sink')
            ).filter(volume__lte=volume_max)

        # Filter based on land use selection (for values > 0)
        selected_land_use = form.cleaned_data.get('land_use')
        if selected_land_use:
            land_use_filter = Q()
            for land_use in selected_land_use:
                land_use_filter |= Q(**{f"{land_use}__gt": 0})
            sinks_queryset = sinks_queryset.filter(land_use_filter)


    context = {
        'form': form,
        'sinks_queryset': sinks_queryset,
    }
    print(len(sinks_queryset), '/n_______SINKS QUERYSET______')
    return render(request, 'toolbox/sink_filter.html', context)


# TODO import DEM to get the Elevation Profile
def elevation_profile(request):
    line_wkt = request.GET.get('line')  # Must be a LINESTRING in WKT
    query = """
        SELECT ST_Value(dem.rast, geom.geom) AS elevation, 
               ST_X(geom.geom) AS lon, 
               ST_Y(geom.geom) AS lat
        FROM dem, 
             (SELECT (ST_DumpPoints(ST_LineFromText(%s, 4326))).geom) AS geom
        WHERE ST_Intersects(dem.rast, geom.geom);
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [line_wkt])
        data = cursor.fetchall()
    
    response = [{'lon': row[1], 'lat': row[2], 'elevation': row[0]} for row in data]
    return JsonResponse(response, safe=False)



#TODO Pegelstände
"""
Hallo Colja,

aus Pegelonline kannst Du viele Pegel abfragen:

R

library(httr)

library(jsonlite)

url <- https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json

response <- GET(url)

data <- fromJSON(content(response, as = "text"))

 

Das Pegelportal betrifft nur die Wassertraßen:

R

library(httr)

library(jsonlite)

url <- https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/KOBLENZ/W/currentmeasurement.json

response <- GET(url)

data <- fromJSON(content(response, "text"))

 

Vielleicht kannst Du auch die Auskunftsplattform Wasser Brandenburg   https://www.metaver.de/trefferanzeige?docuuid=E09AE237-7061-4AD3-AE5A-9D010CF2D231#detail_links

nutzen.

 

Atom-Feed Brandenburg bietet nur statische Geodaten, z. B. hier die Pegelmessstellen: https://metaver.de/search/dls/?serviceId=8CC3E5BE-76AE-4E3A-9456-B8388591170A&datasetId=E28E0202-C62D-46EB-BA13-9CC407FEA2CE
Viele Grüße
Jörg
"""


