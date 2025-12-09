from django.shortcuts import render
from swn import models as swn_models
# from swn import forms as swn_forms
from swn.views import load_nuts_polygon
from . import forms, models, filters

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry, LineString
from django.contrib.gis.measure import D
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models import OuterRef, Subquery
from django.contrib.gis.db.models.functions import Distance,AsGeoJSON
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.forms.models import model_to_dict

from django.template.loader import render_to_string
from django.db import connection
from django.db.models import Max, Min, F, Q
import json, requests
from geo.Geoserver import Geoserver
from requests.auth import HTTPBasicAuth
from datetime import datetime

from shapely.geometry import shape as shapely_shape, mapping
from shapely.ops import nearest_points, transform
from pyproj import Transformer
from collections import defaultdict
import pandas as pd

import numpy as np
import rasterio
import shapefile  # pyshp
import tempfile
import zipfile
import os
import io
import csv
import shutil
from copy import copy

from rasterio.warp import reproject, Resampling, calculate_default_transform, transform_geom
from rasterio.mask import mask
from rasterio.enums import ColorInterp

# TODO DELETE
def test_html(request):
    return render(request, 'toolbox/test.html')
def test_html_2(request):
    return render(request, 'toolbox/test_2.html')

transformer_25833_to_4326 = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
FLOAT32_NODATA = np.float32(-3.4028235e+38)

def boolean_translation(bool, language='de'):
    translation = {
        True: {'de': 'Ja', 'en': 'Yes'},
        False: {'de': 'Nein', 'en': 'No'}
    }
    return translation[bool][language]

def create_feature_collection(queryset, epsg=4326):
    return {
        "type": "FeatureCollection",
        "features": [obj.to_feature(epsg=epsg) for obj in queryset],
        "crs": {
            "type": "name",
            "properties": {"name": f"EPSG:{epsg}"}
        }
    }



def create_point_feature_collection(queryset, epsg=4326):
    return  {
        "type": "FeatureCollection",
        "features": [obj.to_point_feature(epsg=epsg) for obj in queryset],
        "crs": {
            "type": "name",
            "properties": {"name": f"EPSG:{epsg}"}
        }
        }



def toolbox_dashboard(request):
    user = request.user
    project_region = swn_models.ProjectRegion.objects.first().to_feature()

    outline_injection = models.OutlineInjection.objects.first().to_feature()

    outline_surface_water = models.OutlineSurfaceWater.objects.first().to_feature()

    outline_infiltration = models.OutlineInfiltration.objects.first().to_feature()


    counties_form = forms.PolygonSelectionForm(request.POST or None)

    project_form = forms.ToolboxProjectForm(user=user)
    project_modal_title = 'Create new project'

    # default_project = create_default_project(user)

    context = {
        'project_region': project_region,
        # 'default_project': default_project,
        'counties_form': counties_form,
        # 'project_select_form': project_select_form,
        'project_form': project_form,
        'project_modal_title': project_modal_title,
        'outline_injection': outline_injection,
        'outline_surface_water': outline_surface_water,
        'outline_infiltration': outline_infiltration,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)


def save_toolbox_project(request):
    if request.method != 'POST':
        return JsonResponse({'message': {'success': False, 'message': 'Ungültiger Request.'}}, status=405)

    try:
        user = request.user
        request_data = json.loads(request.body)

        toolbox_type = models.ToolboxType.objects.get(name_tag=request_data['toolboxType'])
        user_field = models.UserField.objects.get(pk=request_data['userField'])

        # Known model fields
        known_fields = {'id', 'name', 'description', 'userField', 'toolboxType'}
        project_data = {k: v for k, v in request_data.items() if k not in known_fields}

        # --- UPDATE CASE ---
        if  request_data.get('id'):
            pid = request_data.get('id')
            try:
                project = models.ToolboxProject.objects.get(pk=pid, user=user)
                project.name = request_data.get('name', project.name)
                project.description = request_data.get('description', project.description)
                project.toolbox_type = toolbox_type
                project.user_field = user_field
                project.project_data = project_data
                project.save()

                message = f'Projekt {project.name} wurde aktualisiert.'
                status = 200

            except models.ToolboxProject.DoesNotExist:
                return JsonResponse({'message': {'success': False, 'message': 'Projekt existiert nicht.'}}, status=404)

        # --- CREATE CASE ---
        else:
            project = models.ToolboxProject.objects.create(
                name=request_data['name'],
                user=user,
                toolbox_type=toolbox_type,
                user_field=user_field,
                description=request_data.get('description', ''),
                project_data=project_data
            )
            project.save()
            message = f'Projekt {project.name} wurde gespeichert.'
            status = 201

        return JsonResponse({
            'success': True, 
            'message': message,
            'project': project.to_json(),
        }, status=status)

    except Exception as e:
        print('Error saving project:', e)
        return JsonResponse({'message': {'success': False, 'message': str(e)}}, status=400)
    

def load_toolbox_project(request, id):

    project = models.ToolboxProject.objects.get(pk=id)
    print("Toolbox Project: ", project)
    if not project:
        return JsonResponse({'success': False, 'message': 'Projekt existiert nicht.'})
    else:
        project_json = project.to_json()
        return JsonResponse({'success': True, 'message': f'Projekt {project.name} wurde geladen.', 'project': project_json})

    

@login_required
@csrf_protect
def save_user_field(request):
    if request.method == 'POST':

        if not request.headers.get('X-Csrftoken') == request.COOKIES.get('csrftoken'):
            
            return HttpResponseBadRequest('Invalid CSRF token')
        else:
            
            body = json.loads(request.body)
            name = body['name']
            geom = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            user_field = None
            if body['id']:
                # Update existing UserField
                user_field = models.UserField.objects.get(id=body['id'])
                user_field.name = name
                user_field.geom = geom      
                user_field.filter_bounds = {}
                user_field.save()
            else:
                user_field = models.UserField(name=name,  geom=geom, user=user)
                user_field.save()

            geo_json = user_field.to_feature()
            return JsonResponse(geo_json)      
    else:
        return HttpResponseRedirect('toolbox:toolbox_dashboard')

@login_required
def get_user_fields(request):
    if request.method == "GET":
        user_fields = models.UserField.objects.filter(user=request.user)
        user_projects = models.ToolboxProject.objects.filter(user=request.user)
        ufs = [uf.to_feature() for uf in user_fields]
    return JsonResponse({'user_fields': ufs})


@login_required
# @csrf_protect
def delete_user_field(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            user_field = models.UserField.objects.get(id=id)

            if user_field.user == request.user:
                user_field.delete()
                return JsonResponse({'message': {'success': True, 'message': 'Suchegebiet wurde gelöscht.'}})
            else:
                return JsonResponse({'message': {'success': False, 'message': 'Sie können dieses Suchgebiet nicht löschen.'}}, status=403)

        except models.UserField.DoesNotExist:
            return JsonResponse({'message': {'success': False, 'message': 'Das Suchgebiet konnte nicht gefunden werden.'}}, status=404)
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Ungültiger Request.'}}, status=400)
    
@login_required
def get_field_project_modal(request, id):

    user_field_projects = models.ToolboxProject.objects.filter(
        Q(user_field__id=id) & Q(user_field__user=request.user)
    )

    injection_projects = models.ToolboxProject.objects.filter(
        Q(toolbox_type__name_tag='injection') & Q(user_field__user=request.user)
    )

    # Combine the two querysets
    user_projects = (user_field_projects | injection_projects).order_by('name')
    
    html = render(request, 'toolbox/partials/project_table.html', {'projects': user_projects}).content.decode('utf-8')
    return JsonResponse({'html': html, 'type': 'toolbox'})


#TODO needed here?
def get_options(request, parameter):
    dropdown_list = []
    if parameter == 'toolbox-project':
        toolbox_projects = models.ToolboxProject.objects.filter(user=request.user)
        dropdown_list = [(project.id, project.name) for project in toolbox_projects]
    return JsonResponse({'options': dropdown_list})
        


def add_range_filter(filters, obj, field,  model_field=None):
    model_field = model_field or field
    min_val = obj.get(f'{field}_min')
    max_val = obj.get(f'{field}_max')

    if min_val is not None:
        if model_field == 'index_soil':
            min_val = float(min_val) / 100
        else:
            min_val = float(min_val)
        filters &= Q(**{f"{model_field}__gte": min_val})
    if max_val is not None:
        if model_field == 'index_soil':
            max_val = float(max_val) / 100
        else:
            max_val = float(max_val)
        filters &= Q(**{f"{model_field}__lte": max_val})

    return filters


########## ZALF TOOLBOX ########################

def load_infiltration_gui(request, user_field_id):
    if user_field_id == "null":
         return JsonResponse({'message':{'success': False, 'message': 'Es ist kein Suchgebiet ausgewählt oder es existiert nicht..'}})
    else:
        user_field_id = int(user_field_id)

    start_load_projects = datetime.now()
    toolbox_type = models.ToolboxType.objects.get(name_tag='infiltration')
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    qs = models.ToolboxProject.objects.filter(
        Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
    ).order_by('-creation_date').reverse()
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='infiltration')

    # TODO these querysets are not necessary if the has_x attributes are implemented
    sinks = models.Sink.objects.filter(centroid__within=user_field.geom)    
    
    if user_field.has_infiltration:
        sinks = models.Sink.objects.filter(centroid__within=user_field.geom)
        enlarged_sinks = models.EnlargedSink.objects.filter(centroid__within=user_field.geom)
        streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))
        lakes = models.Lake.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        if user_field.filter_bounds.get('sinks') is None:
            user_field.compute_filter_bounds_infiltration()

        lake_form = filters.LakeFilter(
            request.GET,
            queryset=lakes,
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
        )
        stream_form = filters.StreamFilter(
            request.GET,
            queryset=streams,
            bounds=user_field.filter_bounds.get('streams') if user_field.filter_bounds else None
        )
        sink_form = filters.SinkFilter(
            request.GET,
            queryset=sinks,
            bounds=user_field.filter_bounds.get('sinks') if user_field.filter_bounds else None
        )
        print("Queryset Sinks", sinks.count())
        enlarged_sink_form = filters.EnlargedSinkFilter(
            request.GET,
            queryset=enlarged_sinks,
            bounds=user_field.filter_bounds.get('enlarged_sinks') if user_field.filter_bounds else None
        )

        overall_weighting = forms.OverallWeightingsForm()
        forest_weighting = forms.WeightingsForestForm()
        agriculture_weighting = forms.WeightingsAgricultureForm()
        grassland_weighting = forms.WeightingsGrasslandForm()
        result_form = forms.InfiltrationResultDownloadForm()
        inlet_weighting = forms.InletWeightingsForm()


        html = render_to_string('toolbox/infiltration.html', {
            # 'sink_form': sink_form, 
            # 'enlarged_sink_form': enlarged_sink_form,
            'project_select_form': project_select_form,
            'sink_filter': sink_form,
            'enlarged_sink_filter': enlarged_sink_form,
            'streams_form': stream_form,
            'lakes_form': lake_form,
            'overall_weighting': overall_weighting,
            'forest_weighting': forest_weighting,
            'agriculture_weighting': agriculture_weighting,
            'grassland_weighting': grassland_weighting, 
            'inlet_weighting': inlet_weighting,
            'result_form': result_form,
        }, request=request) 
        default_project = filters.create_default_project(
            user_field, 
            [
                overall_weighting, 
                forest_weighting, 
                agriculture_weighting, 
                grassland_weighting, 
                sink_form, 
                enlarged_sink_form, 
                stream_form, 
                lake_form,
                result_form,
                inlet_weighting,
                ], 
            'infiltration'
            )
        
        return JsonResponse({'success': True, 'html': html, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet sind keine Senken bekannt.'})


def calculate_indices_df(sinks, project, sink_type='sink'):
    w_usability=int(project.get('weighting_overall_usability', 20))/100
    w_soil=int(project.get('weighting_soil_index', 80))/100
    w_fg_fc = int(project.get('weighting_forest_field_capacity', 33.3))/100
    w_fg_hc1= int(project.get('weighting_forest_hydraulic_conductivity_1m', 33.3))/100
    w_fg_hc2= int(project.get('weighting_forest_hydraulic_conductivity_2m', 33.3))/100
    w_ag_fc = int(project.get('weighting_agriculture_field_capacity', 33.3))/100
    w_ag_hydro = int(project.get('weighting_agriculture_hydromorphy', 33.3))/100
    w_ag_soil= int(project.get('weighting_agriculture_soil_type', 33.3))/100
    w_gr_fc = int(project.get('weighting_grassland_field_capacity', 25))/100
    w_gr_hydro = int(project.get('weighting_grassland_hydromorphy', 25))/100
    w_gr_soil = int(project.get('weighting_grassland_soil_type', 25))/100
    w_gr_wet=int(project.get('weighting_grassland_soil_water_ratio', 25))/100

    if sink_type == 'sink':
        model  = models.SinkSoilProperties
        sink_id = 'sink_id'
    elif sink_type == 'enlarged_sink':
        model = models.EnlargedSinkSoilProperties
        sink_id = 'enlarged_sink_id'

    sink_filter_field = f"{sink_type}__in"
    soil_qs = model.objects.filter(**{sink_filter_field: sinks}
        ).select_related(
            sink_type,
            'soil_properties__groundwater_distance',
            'soil_properties__agricultural_landuse',
            'soil_properties__fieldcapacity',
            'soil_properties__hydromorphy',
            'soil_properties__soil_texture',
            'soil_properties__wet_grassland',
        ).values(
            sink_id,
            'percent_of_total_area',
            'soil_properties__groundwater_distance__rating_index',
            'soil_properties__nitrate_contamination',
            'soil_properties__waterlog',
            'soil_properties__agricultural_landuse__name',
            'soil_properties__fieldcapacity__rating_index',
            'soil_properties__hydromorphy__rating_index',
            'soil_properties__soil_texture__rating_index',
            'soil_properties__wet_grassland__rating_index',
            'soil_properties__hydraulic_conductivity_1m_rating',
            'soil_properties__hydraulic_conductivity_2m_rating',
        )

    

    def compute_index_2(row):
        landuse = row['soil_properties__agricultural_landuse__name']
        if landuse == 'grassland':
            return (
                w_gr_fc * row['soil_properties__fieldcapacity__rating_index'] +
                w_gr_hydro * row['soil_properties__hydromorphy__rating_index'] +
                w_gr_soil * row['soil_properties__soil_texture__rating_index'] +
                w_gr_wet * row['soil_properties__wet_grassland__rating_index']
            )
        elif landuse == 'no_agricultural_use':
            return (
                w_fg_fc * row['soil_properties__fieldcapacity__rating_index'] +
                w_fg_hc1 * row['soil_properties__hydraulic_conductivity_1m_rating'] +
                w_fg_hc2 * row['soil_properties__hydraulic_conductivity_2m_rating']
            )
        else:
            return (
                w_ag_fc * row['soil_properties__fieldcapacity__rating_index'] +
                w_ag_hydro * row['soil_properties__hydromorphy__rating_index'] +
                w_ag_soil * row['soil_properties__soil_texture__rating_index']
            )
        
    df= pd.DataFrame.from_records(soil_qs)
    df['bool_general'] = (~df['soil_properties__nitrate_contamination']) & (~df['soil_properties__waterlog'])
    df['index_1'] = df['bool_general'] * df['soil_properties__groundwater_distance__rating_index']
    df['index_2'] = df.apply(compute_index_2, axis=1)
    df['index_be'] = w_usability * df['index_1'] + w_soil * df['index_2']
    df['weighted_index'] = df['index_be'] * df['percent_of_total_area']
    sink_indices = df.groupby(sink_id)['weighted_index'].sum().round(3).to_dict()

    all_indices = {}
    for sink in sinks:
        if sink.index_hydrogeology:
            index_sink_total = (sink_indices[sink.id] + sink.index_proportions + sink.index_feasibility  + sink.index_hydrogeology) / 4  
        else:       
            index_sink_total = (sink_indices[sink.id] + sink.index_proportions + sink.index_feasibility ) / 3
        all_indices[sink.id] = {
            'index_soil': sink_indices[sink.id],
            'index_sink_total': index_sink_total
        }
    print('Indices:', all_indices)
    return all_indices


def filter_sinks(request, sink_type):

    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    if sink_type == 'sink':
        ProjectClass = models.Sink
    else:
        ProjectClass = models.EnlargedSink

    geom = GEOSGeometry(user_field.geom)
    sinks = ProjectClass.objects.filter(geom4326__within=geom)
    print("Sinks:", sinks.count())
    filters = Q()
    filters = add_range_filter(filters, project, f'{sink_type}_area', 'area')
    filters = add_range_filter(filters, project, f'{sink_type}_volume', 'volume')
    filters = add_range_filter(filters, project, f'{sink_type}_depth', 'depth')
    if sink_type == 'enlarged_sink':
        filters = add_range_filter(filters, project, 'enlarged_sink_volume_construction_barrier', 'volume_construction_barrier')
        filters = add_range_filter(filters, project, 'enlarged_sink_volume_gained', 'volume_gained')


    sinks = sinks.filter(filters)

    land_use_values = project.get(f'{sink_type}_land_use', [])
    land_use_values = [int(value) for value in land_use_values if value.isdigit()]
    if sink_type == 'enlarged_sink':
        land_use_filter = (
        Q(landuse_1__in=land_use_values) &
        (Q(landuse_2__in=land_use_values) |
        Q(landuse_2__isnull=True)) &
        (Q(landuse_3__in=land_use_values) |
        Q(landuse_3__isnull=True))&
        (Q(landuse_4__in=land_use_values) |
        Q(landuse_4__isnull=True))
        )
    else:
        land_use_filter = (
            Q(landuse_1__in=land_use_values) &
            (Q(landuse_2__in=land_use_values) |
            Q(landuse_2__isnull=True)) &
            (Q(landuse_3__in=land_use_values) |
            Q(landuse_3__isnull=True))
            )
    sinks = sinks.filter(land_use_filter)
    if sinks.count() == 0:

        message = {
            'success': False, 
            'message': 'Im Suchgebiet entsprechen keine Senken den Filterkriterien.'
        }
        if sink_type == 'enlarged_sink':
            message['message'] = 'Im Suchgebiet entsprechen keine vergrößerten Senken den Filterkriterien.'
        return JsonResponse({'message': message})
    else:
        print("Sinks", sinks.count())
        
        all_indices = calculate_indices_df(sinks, project, sink_type=sink_type)

        features = [sink.to_point_feature(all_indices, language='de') for sink in sinks]
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
        }
        message = {
            'success': True, 
            'message': f'Es wurden {sinks.count()} Senken gefunden.'
        }

        data_info = models.DataInfo.objects.get(data_type=sink_type).to_json()

        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    

def filter_waterbodies(request):

    try:
        request = json.loads(request.body)
        project = request['project']
        data_type = request['dataType']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if data_type in ('lake', 'sieker_lake', 'wetland_lake'):
        waterbody_class = models.Lake
        waterbody = 'Seen'
    elif data_type in ('stream', 'sieker_stream', 'wetland_stream'):
        waterbody = 'Flüsse'
        waterbody_class = models.Stream

    data_info = models.DataInfo.objects.get(data_type=data_type).to_json()

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)

    distance = int(project.get('lake_distance_to_userfield', 0))
    waterbodies = None
    if distance > 0:
        # Transform to EPSG:25833 (meters) and add the buffer
        user_geom_25833 = user_field.geom.transform(25833, clone=True)
        buffer_25833 = user_geom_25833.buffer(distance)
        buffer_4326 = buffer_25833.transform(4326, clone=True)
        waterbodies = waterbody_class.objects.filter(Q(geom__intersects=buffer_4326) | Q(geom__within=buffer_4326))
    else:
        waterbodies = waterbody_class.objects.filter(Q(geom__intersects=geom) | Q(geom__within=geom))

    filter = Q()
    filter = add_range_filter(filter, project, f'{data_type}_min_surplus_volume', 'min_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_mean_surplus_volume', 'mean_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_max_surplus_volume', 'max_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_plus_days', 'plus_days')
    waterbodies = waterbodies.filter(filter)

    if waterbodies.count() == 0:
        
        return JsonResponse({'message': {'success': False, 'message': f'Es befinden sich keine {waterbody} im Suchgebiet die den Filterkriterien entsprechen.'}})
    else:
        
        feature_collection = create_feature_collection(waterbodies)
        
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': {'success': True}})
        



def get_shortest_connection(sink, lakes, streams, epsg=4326, connection_id=0):
    """
    This function works for sinks, enlarged sinks and sieker sinks.
    It returns a dictionary with the sink.id as key and a linefeature with properties as values.
    """
    lake_with_distance = lakes.annotate(
        distance_to_sink=Distance('geom25833', sink.geom25833)
        ).order_by('distance_to_sink').first()
    print('lake_with_distance', lake_with_distance)
    
    stream_with_distance = streams.annotate(
        distance_to_sink=Distance('geom25833', sink.geom25833)
        ).order_by('distance_to_sink').first()
    
    print('stream_with_distance', stream_with_distance)
    
    closest = lake_with_distance if lake_with_distance is not None else stream_with_distance
    print('closest 1', closest)
    if (
        (lake_with_distance and stream_with_distance) and
        (lake_with_distance.distance_to_sink.m > stream_with_distance.distance_to_sink.m)
        ):

        closest = stream_with_distance
    print('closest 2', closest)

    distance_m = int(closest.distance_to_sink.m)
    

    # create a line feature
    pt1, pt2 = nearest_points(
        shapely_shape(json.loads(sink.geom25833.geojson)),
        shapely_shape(json.loads(closest.geom25833.geojson))
    )
    line = LineString([pt1.coords[0], pt2.coords[0]])
    line_geom = GEOSGeometry(line.wkt, srid=25833)

    if epsg==4326:
        line_geom.transform(4326)

    connection_data = {
        'id': connection_id,
        'sink_id': sink.id,  
        'sink_type': sink.__data_type__(),
        'waterbody_type': closest.__data_type__(),
        'waterbody_id': closest.id,
        'fgw_id': closest.fgw_id,
        'waterbody': closest.to_json(),   
        'waterbody_name': closest.name,       
        'distance_m': distance_m,
        'connection_feature': {
            "type": "Feature",
            "geometry": json.loads(line_geom.geojson),
            "properties": {
                'id': connection_id,
                'name': 'Zuleitung',
                'sink_id': sink.id,
                'waterbody_type': closest.__data_type__(),
                'waterbody_id': closest.id,
                'distance_m': distance_m,
            },
        },
    }


    return connection_data


def rate_water_sink_distance(distance):
        if distance >= 2000:
            rating_length = 0
        elif distance >= 1000:
            rating_length = 5
        else:
            rating_length = int((1000 - distance)/10)
        return rating_length
            
def get_infiltration_result_list(project, epsg=4326):
    '''
    this gets the results from an infiltration project. 
    The function is used for display and data download.
    '''

    language='de'
    # the items are ordered by id to ensure that the result ids will be identical if the project is reloaded
    sinks = models.Sink.objects.filter(id__in=project.get('selected_sinks', [])).order_by('id')
    enlarged_sinks = models.EnlargedSink.objects.filter(id__in=project.get('selected_enlarged_sinks', [])).order_by('id')
    lakes = models.Lake.objects.filter(id__in=project.get('selected_lakes', [])).order_by('id')
    streams = models.Stream.objects.filter(id__in=project.get('selected_streams', [])).order_by('id')


    
    
    
    def rate_connection(connection_data, sink, indices):

        index_length = rate_water_sink_distance(connection_data['distance_m'])
        index_volumes = min(connection_data['waterbody']['mean_surplus_volume'] / sink.volume, 1) *100
        print('index_volume', index_volumes)
        if index_length > 0:
            index_inlet = (index_length * int(project.get('weighting_inlet_length', 70)) + index_volumes * int(project.get('weighting_inlet_volume', 30))) / 100
        else:
            index_inlet = 0
        print('index_connection', index_inlet)
        connection_data['connection_feature']['properties']['index_length'] = int(index_length)
        connection_data['index_length'] = round(index_length)
        connection_data['connection_feature']['properties']['index_volumes'] = round(index_volumes)
        connection_data['index_volumes'] = round(index_volumes)
        connection_data['connection_feature']['properties']['index_inlet'] = round(index_inlet)
        connection_data['index_inlet'] = round(index_inlet)
        index_sink = min(int(indices[sink.id]['index_sink_total'] *100), 100)
        connection_data['index_sink'] = index_sink
        if index_inlet > 0:
            index_total = int((index_inlet + index_sink) / 2)
        else:
            index_total = 0
        connection_data['index_total'] = round(index_total)

        return connection_data
    
    result_dict = {}
    results = []
    line_features = []
    sink_count = sinks.count()
    if sink_count > 0:
        indices_sinks = calculate_indices_df(sinks, project, sink_type='sink')
        sink_features = [sink.to_feature(indices_sinks, language='de') for sink in sinks]
        result_dict['sink_feature_collection'] = {
            "type": "FeatureCollection",
            "features": sink_features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
            }
        for i, sink in enumerate(sinks):
            connection_data = get_shortest_connection(sink, lakes, streams, epsg=epsg, connection_id=i)
            connection_data.update({    
                'sink': sink.to_json(indices_sinks),
                'is_enlarged_sink': boolean_translation(False, language),
                })
            connection_data = rate_connection(connection_data, sink, indices_sinks)
            line_feature = connection_data['connection_feature']
            connection_data.pop('connection_feature')
            results.append(connection_data)
            line_features.append(line_feature)
            

    if enlarged_sinks.count() > 0:
        
        indices_enlarged_sinks = calculate_indices_df(enlarged_sinks, project, sink_type='enlarged_sink')
        sink_features = [sink.to_feature(indices_enlarged_sinks, language='de') for sink in enlarged_sinks]
        result_dict['enlarged_sink_feature_collection'] = {
            "type": "FeatureCollection",
            "features": sink_features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
            }
        sink_embankments = models.EnlargedSinkEmbankment.objects.filter(enlarged_sink__in=enlarged_sinks)
        sink_embankment_feature_collection = create_feature_collection(sink_embankments)
        result_dict['sink_embankment_feature_collection'] = sink_embankment_feature_collection
        for i, sink in enumerate(enlarged_sinks):
            connection_data = get_shortest_connection(sink, lakes, streams, epsg=epsg, connection_id=(sink_count + i))

            connection_data.update({
                'sink': sink.to_json(indices_enlarged_sinks),
                'is_enlarged_sink': boolean_translation(True, language),
                })
            connection_data = rate_connection(connection_data, sink, indices_enlarged_sinks)
            line_feature = connection_data['connection_feature']
            connection_data.pop('connection_feature')
            if sink.sink_embankment.exists():
                connection_data['sink_embankment_id'] = sink.sink_embankment.first().id
            # connection_data['sink_feature'] = sink.to_feature(indices_enlarged_sinks, epsg=epsg)
            
            results.append(connection_data)
            line_features.append(line_feature)
        
    result_dict['inlet_feature_collection'] = {
        "type": "FeatureCollection",
        "features": line_features,
        "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
    }
    
    result_dict['results'] = results
    with open('zalf_sink_result_dict.json', 'w') as f:
        json.dump(result_dict, f)

    return result_dict

### NEW 2025-11-15
def get_infiltration_results(request):
    # POST request
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        project = request.body
        project = json.loads(project)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid project JSON'}, status=400)


    results_dict = get_infiltration_result_list(project, epsg=4326)
    result_data_info = models.DataInfo.objects.get(data_type='infiltration_result').to_json()
    inlet_data_info = models.DataInfo.objects.get(data_type='infiltration_result_inlet').to_json()
    sink_data_info = models.DataInfo.objects.get(data_type='infiltration_result_sink').to_json()
    enlarged_sink_data_info = models.DataInfo.objects.get(data_type='infiltration_result_enlarged_sink').to_json()
    lake_data_info = models.DataInfo.objects.get(data_type='lake').to_json()
    stream_data_info = models.DataInfo.objects.get(data_type='stream').to_json()
    sink_embankment_data_info = models.DataInfo.objects.get(data_type='sink_embankment').to_json()

    response = {
        'inlet_data_info': inlet_data_info,
        'sink_data_info': sink_data_info,
        'enlarged_sink_data_info': enlarged_sink_data_info,
        'result_data_info': result_data_info,
        'lake_data_info': lake_data_info,
        'stream_data_info': stream_data_info,
        'sink_embankment_data_info': sink_embankment_data_info,

        'results': results_dict['results'],

        'inlet_feature_collection': results_dict.get('inlet_feature_collection', None),
        'sink_feature_collection' : results_dict.get('sink_feature_collection', None),
        'enlarged_sink_feature_collection': results_dict.get('enlarged_sink_feature_collection', None),
        'sink_embankment_feature_collection': results_dict.get('sink_embankment_feature_collection', None),

        'message': {
            'success': True,
        }
    }

    return JsonResponse(response)
    # except:

    #     return JsonResponse({'message': {'success': False, 'message': 'Get results failed.'}})


def get_injection_volume_chart(request, waterbody_type, id):
    """
    Gets injection volume chart data for a given waterbody type and ID.
    """
    if waterbody_type == 'stream':
        wb = models.Stream.objects.get(pk=id)
    elif waterbody_type == 'lake':
        wb = models.Lake.objects.get(pk=id)

    chart_data_qs = (
        models.DischargeTimeseries.objects
        .filter(fgw=wb.fgw)
        .order_by('date')
        .values('date', 'discharge_m3s')
    )

    chart_data = [
        {
            "x": record["date"].isoformat(),     # ISO 8601 — ideal for JS Date parsing
            "y": float(record["discharge_m3s"] or 0)
        }
        for record in chart_data_qs
    ]

    return JsonResponse({"chart_data": chart_data})

# TODO DEM fehlt noch
def get_elevation_profile(line_geojson):
    """
    Gets an elevation profile in a 20m raster for a given line geometry.
    Returns a list of dictionaries with {'dist': 20.0, 'nr': 1, 'x': 451082.0, 'y': 5758479.0, 'z': 60.7175178527832}.
    """
    start = datetime.datetime.now()
    url = "https://isk.geobasis-bb.de/elevation/geojson/line"  
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(line_geojson))

    if response.status_code == 200:
        elevation_data = response.json()
        return {'success': True, 'data': elevation_data}
    else:
        return {'success': False, 'error': f'Error{response.status_code}: {response.text}'}
    
# not in use
def get_elevations_for_line(line_geom):
    sql = """
    SELECT
      ST_Value(rast, 1, pt.geom) AS elevation,
      ST_AsText(pt.geom) AS point
    FROM (
      SELECT (ST_DumpPoints(ST_Segmentize(ST_GeomFromText(%s, 25833), 1))).geom
    ) pt,
    dem
    WHERE ST_Intersects(rast, pt.geom);
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [line_geom.wkt])
        return cursor.fetchall()


###### Zalf infiltration end #################################


####### SIEKER TOOLBOX ########################

##### Surface Waters ######
def load_sieker_surface_waters_gui(request, user_field_id):
    if user_field_id == "null":

        return JsonResponse({'message':{'success': False, 'message': 'Das Suchgebiet konnte nicht gefunden werden.'}})
    else:
        user_field_id = int(user_field_id)

    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))        
    
    lakes = models.SiekerLargeLake.objects.filter(Q(geom4326__within=user_field.geom) | Q(geom4326__intersects=user_field.geom))

    if lakes.count() > 0:
        toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_surface_water')
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='sieker_surface_water')
        sieker_lake_filter = filters.SiekerLargeLakeFilter(
            request.GET,
            queryset=lakes,
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
            )

        
        result_form = forms.SiekerSurfaceWaterResultDownloadForm()


        


        default_project = filters.create_default_project(
            user_field, 
            [
                sieker_lake_filter, 
                result_form
            ], 
            'sieker_surface_water'
            )
        

        html = render_to_string('toolbox/sieker_surface_waters.html', {
            'project_select_form': project_select_form,
            'sieker_lake_filter': sieker_lake_filter,   
            'result_form': result_form,   
        }, request=request) 

        return JsonResponse({'success': True,  'html': html, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet befinden sich keine geeigneten Seen.'})

    
def get_water_levels(request, user_field_id):
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))        

    water_levels = models.SiekerWaterLevel.objects.filter(
            geom4326__within=user_field.geom
        )
    if water_levels.count() == 0:
        return JsonResponse({'message': {'success': False, 'message': 'Im Suchgebiet existieren keine Pegel.'}})
    
    water_levels_feature_collection = create_feature_collection(water_levels)
    water_levels_data_info = models.DataInfo.objects.get(data_type='sieker_water_level').to_json()

    water_levels = {
                'featureCollection': water_levels_feature_collection,
                'dataInfo': water_levels_data_info
                }
    return JsonResponse({'water_levels':water_levels, 'message': {'success': True}})


def filter_sieker_surface_waters(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])

    lakes_data_info = models.DataInfo.objects.get(data_type='sieker_surface_water').to_json()
    lakes = models.SiekerLargeLake.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    filter = Q()
    filter = add_range_filter(filter, project, 'sieker_surface_water_area_ha', 'area_ha')
    filter = add_range_filter(filter, project, 'sieker_surface_water_vol_mio_m3', 'vol_mio_m3')
    filter = add_range_filter(filter, project, 'sieker_surface_water_d_max_m', 'd_max_m')
    lakes = lakes.filter(filter)


    print("COUNT(Lakes)", lakes.count())

    if lakes.count() == 0:
        
        return JsonResponse({'message': {'success': False, 'message': 'Keine Seen im Suchgebiet entsprechen den Filterkriterien.'}})
    else:
        
        lakes_feature_collection = create_feature_collection(lakes)
        message = {
            'success': True, 
        }
        lakes = {
                'featureCollection':lakes_feature_collection,
                'dataInfo': lakes_data_info
            }
        return JsonResponse({'lakes': lakes, 'message': message})
    

def get_all_sieker_surface_waters(request):
    """
    Filter excludes lakes with missing data, therefore this
    """
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])

    lakes_data_info = models.DataInfo.objects.get(data_type='sieker_surface_water').to_json()
    lakes = models.SiekerLargeLake.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    if lakes.count() == 0:
        
        return JsonResponse({'message': {'success': False, 'message': 'Keine Seen im Suchgebiet entsprechen den Filterkriterien.'}})
    else:
        
        lakes_feature_collection = create_feature_collection(lakes)
        message = {
            'success': True, 
        }
        lakes = {
                'featureCollection':lakes_feature_collection,
                'dataInfo': lakes_data_info
            }
        # print("{'lakes': lakes, 'message': message}", {'lakes': lakes, 'message': message})
        return JsonResponse({'lakes': lakes, 'message': message})


def get_sieker_surface_water_levels(request, id):  
    sieker_station = models.SiekerWaterLevel.objects.get(id=id)
    station = sieker_station.station

    chart_data_qs = (
        models.TimeseriesDailyWaterlevel.objects
        .filter(station=station)
        .order_by('date')
        .values('date', 'level')
    )

    chart_data = [
        {
            "x": record["date"].isoformat(),    
            "y": float(record["level"] or 0)
        }
        for record in chart_data_qs
    ]
    return JsonResponse({"chart_data": chart_data, "station_name": sieker_station.name})

def get_all_above_ground_catchment_areas(request):
    """
    Get all above ground catchments in the area
    """
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])

    catchment_info = models.DataInfo.objects.get(data_type='above_ground_catchment_area').to_json()
    catchments = models.AboveGroundCatchmentArea.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    if catchments.count() == 0:
        
        return JsonResponse({'message': {'success': False, 'message': 'Es sind keine Einzugsgebiete in Ihrem Suchgebiet in der Datenbank hinterlegt.'}})
    else:
        
        catchment_feature_collection = create_feature_collection(catchments)
        message = {
            'success': True, 
        }
        catchments = {
                'featureCollection':catchment_feature_collection,
                'dataInfo': catchment_info
            }
        return JsonResponse({'catchments': catchments, 'message': message})

##### Sieker Sinks ######
   
def load_sieker_sink_gui(request, user_field_id):
    if user_field_id == "null":
        return JsonResponse({'message':{'success': False, 'message': 'Es ist kein Suchgebiet ausgewählt oder es existiert nicht.'}})
    else:
        user_field_id = int(user_field_id)
    toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_sink')
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))


    qs = models.ToolboxProject.objects.filter(
        Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='sieker_sink')
    
    sinks = models.SiekerSink.objects.filter(
        centroid__within=user_field.geom
    )

    if sinks.count() > 0:
        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        sieker_sink_filter = filters.SiekerSinkFilter(
            request.GET, 
            queryset=sinks,
            bounds=user_field.filter_bounds.get('sieker_sinks') if user_field.filter_bounds else None
            )
        
        streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))
        lakes = models.Lake.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        lake_form = filters.LakeFilter(
            request.GET,
            queryset=lakes,
            prefix='sieker_lake',
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
        )
        stream_form = filters.StreamFilter(
            request.GET,
            queryset=streams,
            prefix='sieker_stream',
            bounds=user_field.filter_bounds.get('streams') if user_field.filter_bounds else None
        )

        result_form = forms.SiekerSinkDownloadForm()

        default_project = filters.create_default_project(
            user_field,
            [
                sieker_sink_filter, 
                lake_form, 
                stream_form,
                result_form,
                ],
            'sieker_sink'
        )
        print(default_project)

        html = render_to_string('toolbox/sieker_sink.html', {
            'project_select_form': project_select_form,
            'sieker_sink_filter': sieker_sink_filter,
            'lakes_form': lake_form,
            'streams_form': stream_form,
            'result_form': result_form,

        }, request=request) 

        return JsonResponse({'success': True, 'html': html, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet sind keine Senken bekannt.'})


def filter_sieker_sinks(request):

    start = datetime.now()
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    
    geom = GEOSGeometry(user_field.geom)
    
    sinks = models.SiekerSink.objects.filter(geom4326__within=geom)

    filters = Q()
    filters = add_range_filter(filters, project, 'sieker_sink_area', 'area')
    filters = add_range_filter(filters, project, 'sieker_sink_volume', 'volume')
    filters = add_range_filter(filters, project, 'sieker_sink_avg_depth', 'avg_depth')
    filters = add_range_filter(filters, project, 'sieker_sink_depth', 'depth')
    filters = add_range_filter(filters, project, 'sieker_sink_urbanarea_percent', 'urbanarea_percent')
    filters = add_range_filter(filters, project, 'sieker_sink_wetlands_percent', 'wetlands_percent')
    
    sinks = sinks.filter(filters)

    feasibility = project.get('sieker_sink_feasibility', [])

    sinks = sinks.filter(Q(umsetzbark__in=feasibility))

    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': 'Im Suchgebiet entsprechen keine Senken den Filterkriterien.'
        }
        return JsonResponse({'message': message})
    else:
        
        data_info = models.DataInfo.objects.get(data_type='sieker_sink').to_json()
        feature_collection = create_point_feature_collection(sinks)
        message = {
            'success': True, 
            'message': f'Es wurden {sinks.count()} Senken gefunden.'
        }
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    

def get_sieker_sink_result_list(sinks, lakes, streams, epsg=4326):
    '''
    this gets the results from a sieker sink project. 
    '''

    language='de'
    # the items are ordered by id to ensure that the result ids will be identical if the project is reloaded

    def rate_connection(connection_data, sink):
        index_length = rate_water_sink_distance(connection_data['distance_m'])
        index_volumes = min(connection_data['waterbody']['mean_surplus_volume'] / sink.volume, 1) *100
        print('index_volume', index_volumes)

        connection_data['connection_feature']['properties']['index_length'] = int(index_length)
        connection_data['index_length'] = round(index_length)
        connection_data['connection_feature']['properties']['index_volumes'] = round(index_volumes)
        connection_data['index_volumes'] = round(index_volumes)
        connection_data['umsetzbark'] = sink.umsetzbark

        return connection_data

    results = []
    line_features = []

    for i, sink in enumerate(sinks):
        connection_data = get_shortest_connection(sink, lakes, streams, epsg=epsg, connection_id=i)
        connection_data.update({'sink': sink.to_json()})
        connection_data = rate_connection(connection_data, sink)
        line_feature = connection_data['connection_feature']
        connection_data.pop('connection_feature')
        results.append(connection_data)
        line_features.append(line_feature)
   

    sink_feature_collection = create_feature_collection(sinks)
    result_dict= {
        'sink_feature_collection': sink_feature_collection,
        'inlet_feature_collection': {
            "type": "FeatureCollection",
            "features": line_features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
        },
        'results': results,
    }
    with open('sieker_sink_result_dict.json', 'w') as f:
        json.dump(result_dict, f)

    return result_dict

def get_sieker_sink_results(request):
    # POST request
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        project = request.body
        print('Project:', type(project))
        project = json.loads(project)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid project JSON'}, status=400)
    sinks = models.SiekerSink.objects.filter(id__in=project.get(f'selected_sieker_sinks', []))
    lakes = models.Lake.objects.filter(id__in=project.get(f'selected_sieker_lakes', []))
    streams = models.Stream.objects.filter(id__in=project.get(f'selected_sieker_streams', []))

    results_dict = get_sieker_sink_result_list(sinks, lakes, streams, epsg=4326)
    result_data_info = models.DataInfo.objects.get(data_type='sieker_sink_result').to_json()
    inlet_data_info = models.DataInfo.objects.get(data_type='sieker_sink_result_inlet').to_json()
    sink_data_info = models.DataInfo.objects.get(data_type='sieker_sink_result_sink').to_json()
    lake_data_info = models.DataInfo.objects.get(data_type='lake').to_json()
    lake_data_info['dataType'] = 'sieker_lake'

    stream_data_info = models.DataInfo.objects.get(data_type='stream').to_json()
    stream_data_info['dataType'] = 'sieker_stream'

    response = {
        'inlet_data_info': inlet_data_info,
        'sink_data_info': sink_data_info,
        'result_data_info': result_data_info,
        'lake_data_info': lake_data_info,
        'stream_data_info': stream_data_info,
        'results': results_dict['results'],
        'inlet_feature_collection': results_dict.get('inlet_feature_collection', None),
        'sink_feature_collection' : results_dict.get('sink_feature_collection', None),
    
        'message': {
            'success': True,
        }
    }
    return JsonResponse(response)

##### Sieker Gewässerentwicklungskonzepte ######
def load_sieker_gek_gui(request, user_field_id):
    if user_field_id == "null":
         return JsonResponse({'message':{'success': False, 'message': 'Es ist kein Suchgebiet ausgewählt oder es existiert nicht.'}})
    else:
        user_field_id = int(user_field_id)
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))

    geks = models.GekRetention.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    # all_sieker_gek_ids = [g.id for g in geks]
   

    if geks.count() > 0:
        toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_gek')
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='sieker_gek')

        feature_collection = create_feature_collection(geks)

        gek_filter_form = filters.GekRetentionFilter(
            request.GET, 
            queryset=geks,
            bounds=user_field.filter_bounds.get('sieker_geks') if user_field.filter_bounds else None
            )
        slider_labels = dict(models.GekPriority.objects.values_list("priority_level", "description_de").distinct().order_by("priority_level"))

        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        # sieker_geks_filter = SiekerGekFilter(request.GET, queryset=geks)

        result_form = forms.SiekerGekDownloadForm()
        default_project = filters.create_default_project(
            user_field,
            [
                gek_filter_form,
                result_form,
                ],
            'sieker_gek'
        )
        default_project['all_sieker_gek_ids'] = list(geks.values_list('id', flat=True))
        default_project['selected_sieker_geks'] = default_project['all_sieker_gek_ids']

        html = render_to_string('toolbox/sieker_gek.html', {
            'project_select_form': project_select_form,
            'gek_filter_form': gek_filter_form ,
            'result_form': result_form,
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_json()

        return JsonResponse({'success': True, 'html': html, 'featureCollection': feature_collection, 'slider_labels': slider_labels, 'dataInfo': data_info, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet sind keine Gewässerentwicklungskonzepte verfügbar.'})



def get_all_sieker_geks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user_field = models.UserField.objects.get(pk=project['userField'])
    geks = models.GekRetention.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    if geks.count() == 0:
        return JsonResponse({'message': {'success': False, 'message': 'Im Suchgebiet sind keine Gewässerentwicklungskonzepte bekannt.'}})
    
    feature_collection = create_feature_collection(geks)
    data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_json()

    return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': {'success': True}})

def get_geks_and_measures(project):
    ids = project.get('selected_sieker_geks')
    geks = models.GekRetention.objects.filter(pk__in=ids)
    landuses = models.GekLanduse.objects.filter(Q(gek_retention__in=geks) & Q(clc_landuse__id__in=project['gek_landuse']))
    geks = models.GekRetention.objects.filter(landuses__in=landuses).distinct()
    print("Geks:", geks.count())

    # filter measures
    filters = Q(priority_value__gte=project['gek_priority'])
    filters = add_range_filter(filters, project, 'gek_costs', 'costs') 

    measures = models.GekRetentionMeasure.objects.filter(
            gek_retention__in=geks
        ).filter(filters)
    
    geks = models.GekRetention.objects.filter(measures__in=measures).distinct()
    return geks, measures

# TODO: turn into filter gek
def filter_sieker_geks(request):
   # add_range_filter(filters, obj, field,  model_field=None)
    start = datetime.now()
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    # filter landuses
    print('Project', project)
    
    geks, measures = get_geks_and_measures(project)

    if geks.count() == 0:
        message = {
            'success': False, 
            'message': f'Es sind keine Gewässerentwicklungskonzepte für diese Filtereinstellungen bekannt.'
        }
        return JsonResponse({'message': message})
    else:
        print("Geks", geks.count())
        
        feature_collection = create_feature_collection(geks)

        dict_list = []
        for gek in geks:
            d = gek.to_json()
            d['measures'] = [m.to_json() for m in measures if m.gek_retention == gek]
            dict_list.append(d)

        features = []
        for gek in geks:
            feature = gek.to_feature()
            feature['properties']['measures'] = [m.to_json() for m in measures if m.gek_retention == gek]
            features.append(feature)

        print('measures: ', dict_list)
        feature_collection['features'] = features

        data_info = models.DataInfo.objects.get(data_type='filtered_sieker_gek').to_json()
        print('Time for filter_sinks:', datetime.now() - start)
        
        return JsonResponse({'featureCollection': feature_collection, 'message' : {'success': True}, 'dataInfo': data_info, 'measures': dict_list})


# Sieker Wetlands

   
def load_sieker_wetland_gui(request, user_field_id):
    if user_field_id == "null":
         return JsonResponse({'message':{'success': False, 'message': 'Es ist kein Suchgebiet ausgewählt oder es existiert nicht..'}})
    else:
        user_field_id = int(user_field_id)

    user = request.user
    toolbox_type = models.ToolboxType.objects.get(name_tag='wetland')
    user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))
    
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    
    wetlands = models.HistoricalWetlands.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    if wetlands.count() > 0:
        qs = models.ToolboxProject.objects.filter(
                Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='wetland')
        
        feature_collection = create_feature_collection(wetlands)
        filter_form = filters.HistoricalWetlandsFilter()
        slider_labels =  dict(models.WetlandFeasibility.objects.values_list('id', 'name_de').order_by('id'))
        streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))
        lakes = models.Lake.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        lake_form = filters.LakeFilter(
            request.GET,
            queryset=lakes,
            prefix='wetland_lake',
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
        )
        stream_form = filters.StreamFilter(
            request.GET,
            queryset=streams,
            prefix='wetland_stream',
            bounds=user_field.filter_bounds.get('streams') if user_field.filter_bounds else None
        )
        # TODO This does not really make sense - more filters?
        result_form = forms.SiekerWetlandDownloadForm()

        default_project = filters.create_default_project(
            user_field,
            [
                filter_form,
                lake_form,
                stream_form,
                result_form,
                ],
            'wetland'
        )
        default_project['selected_wetlands'] = list(wetlands.values_list('id', flat=True))

        html = render_to_string('toolbox/sieker_wetlands.html', {
            'project_select_form': project_select_form,
            'wetlands_filter': filter_form,
            'lakes_form': lake_form,
            'streams_form': stream_form,
            'result_form': result_form,
            
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='wetland').to_json()

        return JsonResponse({'success': True, 'html': html, 'featureCollection': feature_collection,  'dataInfo': data_info, 'slider_labels': slider_labels, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet sind keine historischen Feuchtgebiete bekannt.'})



#TODO
def filter_sieker_wetlands(request):
   # add_range_filter(filters, obj, field,  model_field=None)
    start = datetime.now()
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    print('FROM filter_wetlands project', project)
    
    # filter landuses
    ids = project.get('selected_wetlands')
    wetlands = models.HistoricalWetlands.objects.filter(pk__in=ids)

    # filter measures
    filters = Q(priority__priority_level__gte=project['feasibility'])
    filters = add_range_filter(filters, project, 'wetland_costs', 'costs') 
    print("Weltlands FILTERED:", wetlands.count())


    if wetlands.count() == 0:
        message = {
            'success': False, 
            'message': f'Es sind keine Gewässerentwicklungskonzepte für diese Filtereinstellungen bekannt.'
        }
        return JsonResponse({'message': message})
    else:
        print("wetlands", wetlands.count())
        
        feature_collection = create_feature_collection(wetlands)
        data_info = models.DataInfo.objects.get(data_type='wetland').to_json()
 
        return JsonResponse({'featureCollection': feature_collection, 'message' : {'success': True}, 'dataInfo': data_info})



def get_sieker_wetland_result_list(wetlands, lakes, streams, epsg=4326):
    '''
    this gets the results from a sieker wetland project. 
    '''

    language='de'
    # the items are ordered by id to ensure that the result ids will be identical if the project is reloaded

    def rate_connection(connection_data, wetland):
        index_length = rate_water_sink_distance(connection_data['distance_m'])
        # index_volumes = min(connection_data['waterbody']['mean_surplus_volume'] / wetland.volume, 1) *100
        # print('index_volume', index_volumes)

        connection_data['connection_feature']['properties']['index_length'] = int(index_length)
        connection_data['index_length'] = round(index_length)
        # connection_data['connection_feature']['properties']['index_volumes'] = round(index_volumes)
        # connection_data['index_volumes'] = round(index_volumes)
        connection_data['feasibility'] = wetland.feasibility.name_de if language == 'de' else wetland.feasibility.name_en

        return connection_data

    results = []
    line_features = []

    for i, wetland in enumerate(wetlands):
        connection_data = get_shortest_connection(wetland, lakes, streams, epsg=epsg, connection_id=i)
        connection_data.update({'sink': wetland.to_json()})
        connection_data = rate_connection(connection_data, wetland)
        line_feature = connection_data['connection_feature']
        connection_data.pop('connection_feature')
        results.append(connection_data)
        line_features.append(line_feature)
   

    wetland_feature_collection = create_feature_collection(wetlands)
    result_dict= {
        'sink_feature_collection': wetland_feature_collection,
        'inlet_feature_collection': {
            "type": "FeatureCollection",
            "features": line_features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
        },
        'results': results,
    }
    with open('sieker_wetland_result_dict.json', 'w') as f:
        json.dump(result_dict, f)

    return result_dict


def get_sieker_wetland_results(request):
    # POST request
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        project = request.body
        print('Project:', type(project))
        project = json.loads(project)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid project JSON'}, status=400)

    wetlands = models.HistoricalWetlands.objects.filter(id__in=project.get(f'selected_wetlands', []))
    lakes = models.Lake.objects.filter(id__in=project.get(f'selected_wetland_lakes', []))
    streams = models.Stream.objects.filter(id__in=project.get(f'selected_wetland_streams', []))

    results_dict = get_sieker_wetland_result_list(wetlands, lakes, streams, epsg=4326)
    result_data_info = models.DataInfo.objects.get(data_type='wetland_result').to_json()
    inlet_data_info = models.DataInfo.objects.get(data_type='sieker_sink_result_inlet').to_json()
    inlet_data_info['dataType'] = 'wetland_result_inlet'
    wetland_data_info = models.DataInfo.objects.get(data_type='wetland').to_json()
    wetland_data_info['dataType'] = 'wetland_result_wetland'
    lake_data_info = models.DataInfo.objects.get(data_type='lake').to_json()
    lake_data_info['dataType'] = 'wetland_lake'

    stream_data_info = models.DataInfo.objects.get(data_type='stream').to_json()
    stream_data_info['dataType'] = 'wetland_stream'

    response = {
        'inlet_data_info': inlet_data_info, #inletDataInfo
        'wetland_data_info': wetland_data_info, # sinkDataInfo.sink
        'result_data_info': result_data_info, # in js dataInfo
        'lake_data_info': lake_data_info, # waterbodyDataInfo.lake
        'stream_data_info': stream_data_info, # waterbodyDataInfo.stream
        'results': results_dict['results'], # inlets
        'inlet_feature_collection': results_dict.get('inlet_feature_collection', None),
        'sink_feature_collection' : results_dict.get('sink_feature_collection', None),
    
        'message': {
            'success': True,
        }
    }
    return JsonResponse(response)
    

def load_injection_gui(request):
    user = request.user
    toolbox_type = models.ToolboxType.objects.get(name_tag='injection')
    
    qs = models.ToolboxProject.objects.filter(
            Q(user=user)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
    
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='injection')
    injection_weightings_form = forms.MarWeightingForm()
    suitability_aquifer_thickness = forms.SuitabilityForm('aquifer_thickness')
    suitability_depth_groundwater_form = forms.SuitabilityForm('depth_groundwater')
    suitability_land_use_form = forms.SuitabilityForm('land_use')
    suitability_distance_to_source_form = forms.SuitabilityForm('distance_to_source')
    suitability_distance_to_well_form = forms.SuitabilityForm('distance_to_well')
    suitability_hydraulic_conductivity = forms.SuitabilityForm('hydraulic_conductivity')

    slider_labels = dict(models.MarSliderDescription.objects.values_list('id', 'name_de').order_by('id'))
    slider_labels_suitability = dict(models.MarSuitabilitySliderDescription.objects.values_list('id', 'name_de').order_by('id'))

    result_form = forms.InjectionDownloadForm()

    html = render_to_string('toolbox/injection.html', {
        # 'sink_form': sink_form, 
        # 'enlarged_sink_form': enlarged_sink_form,
        
        'project_select_form': project_select_form,
        'injection_weightings_form': injection_weightings_form,
        'suitability_aquifer_thickness': suitability_aquifer_thickness,
        'suitability_depth_groundwater_form': suitability_depth_groundwater_form, 
        'suitability_land_use_form': suitability_land_use_form,
        'suitability_distance_to_source_form': suitability_distance_to_source_form,
        'suitability_distance_to_well_form': suitability_distance_to_well_form,
        'suitability_hydraulic_conductivity': suitability_hydraulic_conductivity,
        'result_form': result_form,

    }, request=request) 
    default_project = filters.create_default_project(
        None, 
        [
            injection_weightings_form, 
            suitability_aquifer_thickness, 
            suitability_depth_groundwater_form, 
            suitability_land_use_form, 
            suitability_distance_to_source_form, 
            suitability_distance_to_well_form, 
            suitability_hydraulic_conductivity,
            result_form,
        ],
        'injection'
        )

    return JsonResponse({'success': True, 'html': html, 'slider_labels': slider_labels, 'slider_labels_suitability': slider_labels_suitability, 'default_project': default_project})

def delete_geoserver_layer(workspace, layer_name):
    """
    Clears GeoWebCache tiles for a specific layer in GeoServer.
    """
    url = f"{settings.GEOSERVER_URL}/gwc/rest/layers/{workspace}:{layer_name}.xml"
    
    try:
        r = requests.delete(
            url,
            auth=HTTPBasicAuth(settings.GEOSERVER_USER, settings.GEOSERVER_PASS),
        )

        if r.status_code in (200, 202, 204):
            print(f"Cache for {workspace}:{layer_name} cleared successfully")
        elif r.status_code == 404:
            print(f"Failed to clear cache: {r.status_code} - {r.text}")
            r.raise_for_status()
        else:
            print(f"Failed to clear cache: {r.status_code} - {r.text}")
            r.raise_for_status()
    except:
        pass


def publish_raster_on_geoserver(layer_name, workspace='spreewassern_raster', style_name="style_raster_percent_sieker_2"):
    """
    Publishes a GeoTIFF to GeoServer as a coverage store and attaches an existing style.
    """

    geo = Geoserver(
        settings.GEOSERVER_URL,
        username=settings.GEOSERVER_USER,
        password=settings.GEOSERVER_PASS
    )

    geo.create_coveragestore(layer_name=layer_name, path=f'/app/raster_data/{layer_name}.tif', workspace=workspace)
    geo.publish_style(layer_name=layer_name, style_name=style_name, workspace=workspace)



def compute_suitability_from_tifs(suitability_dict, user):
    FLOAT32_NODATA = np.float32(-3.4028235e+38)

    with rasterio.open('raster_data/no_injection_area_mask_v2.tif') as mask:
        nogo_mask = mask.read(1)
        mask_nodata = mask.nodata
        mask_width = mask.width
        mask_height = mask.height
        mask_profile = mask.profile.copy()

    nogo_mask = np.where(nogo_mask == mask_nodata, np.nan, nogo_mask)

    length_stack = len(suitability_dict)
    stack = np.zeros((length_stack, mask_height, mask_width), dtype=np.float32)
    weighted_stack = np.zeros((mask_height, mask_width), dtype=np.float32)


    layer_weight_sum = 0
    for key in suitability_dict:
        layer_weight_sum += suitability_dict[key]['weight']
        
    i = 0
    for key in suitability_dict:
        
        path = suitability_dict[key]['map_path']
        
        # try:
        with rasterio.open(path) as src:
            dst_arr = src.read(1)  
            dst_nodata = src.nodata
        new_arr = np.where(dst_arr == dst_nodata, np.nan, dst_arr).astype(np.float32)

        for k in suitability_dict[key]['mapping']:
            new_arr = np.where(
                new_arr==float(suitability_dict[key]['mapping'][k]['map_value']),
                suitability_dict[key]['mapping'][k]['score'],
                new_arr
                )
        stack[i] = new_arr
        weighted_stack = weighted_stack + (new_arr * suitability_dict[key]['weight'] / layer_weight_sum)
        
        i +=1

    result_2d = weighted_stack * 100
    result_2d = np.where(nogo_mask == 0, 0, result_2d)
    result_2d = np.where(np.isnan(result_2d), np.nan, np.clip(result_2d, 0, 100))
    result_2d_to_write = np.where(np.isnan(result_2d), FLOAT32_NODATA, result_2d).astype(np.float32)

    with rasterio.open(f'raster_data/{user.id}_mar_result.tif', 'w', **mask_profile) as f:

        f.write(result_2d_to_write.astype(np.float32),1)

    i = 0
    for key in suitability_dict:
        stack_to_write = np.where(np.isnan(stack[i]), FLOAT32_NODATA, stack[i]).astype(np.float32)
        print(i)
        with rasterio.open(f'raster_data/{user.id}_weighted_stack_{key}.tif', 'w', **mask_profile) as f:

            f.write(stack_to_write.astype(np.float32),1)
        i += 1
    
    publish_raster_on_geoserver(f"{user.id}_mar_result")



        
def mar_calculate_area(request):
    user = request.user
    if request.method == 'POST':
        project = json.loads(request.body)
        print('Project:', project)

        map_labels = models.MapLabels.objects.all()
        suitability_dict = {}
        for label in map_labels:
            suitability = label.suitability
            name = label.name
            map_value = label.map_value
            default_score = label.default_score
            if suitability not in suitability_dict:
                suitability_dict[suitability] = {'mapping': {}}
            suitability_dict[suitability]['map_path'] = 'raster_data/' + label.map_name
            suitability_dict[suitability]['weight'] = int(project.get(f'weighting_{suitability}', 5))/5
            suitability_dict[suitability]['mapping'][name] = {
                'map_value': map_value,
                'default_score': default_score/5,
                'score': int(project.get(f'{suitability}_{name}', default_score))/5,
                }

        compute_suitability_from_tifs(suitability_dict, user)


        return JsonResponse({'success': True})
    

################### BELOW IS NOT IN USE AND NOT WORKING ###############
# from django.http import HttpResponse, JsonResponse
ALLOWED_WMS_PARAMS = {
    "service",
    "request",
    "version",
    "layers",
    "layer",
    # "styles",
    "bbox",
    "width",
    "height",
    "srs",
    "crs",
    "format",
    "transparent",
    
    "qcl_filter",
}

def geoserver_wms(request):
    geoserver_url = f"{settings.GEOSERVER_URL}/spreewassern_raster/wms"

    params = request.GET.dict()

    # Keep only allowed WMS params
    wms_params = {k: v for k, v in params.items() if k.lower() in ALLOWED_WMS_PARAMS}

    response = requests.get(
        geoserver_url,
        params=wms_params,
    )

    return HttpResponse(
        response.content,
        content_type=response.headers.get("Content-Type")
    )


COLORMAP_RED_GREEN = [
    (0, "#d7191c"),
    (25, "#fdae61"),
    (50, "#ffffc0"),
    (75, "#a6d96a"),
    (100, "#1a9641")
]

COLORMAP_BLUE_BROWN = [
    (0, "#2b83ba"),    # watery blue
    (25, "#abd9e9"),   # light blue / wet
    (50, "#ffffbf"),   # beige / neutral
    (75, "#fdae61"),   # light brown / drier
    (100, "#8c510a")   # dark brown / very dry
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def interpolate_color(val, colormap):
    # Find the two surrounding entries
    for i in range(len(colormap) - 1):
        q1, c1 = colormap[i]
        q2, c2 = colormap[i + 1]
        if q1 <= val <= q2:
            ratio = (val - q1) / (q2 - q1)
            r1, g1, b1 = hex_to_rgb(c1)
            r2, g2, b2 = hex_to_rgb(c2)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            return rgb_to_hex((r, g, b))
    # If outside range, clamp
    if val < colormap[0][0]:
        return colormap[0][1]
    return colormap[-1][1]

def geoserver_wms_sld(request):
    geoserver_url = f"{settings.GEOSERVER_URL}/spreewassern_raster/wms"
    params = request.GET.dict()
    threshold = float(params.get("threshold", 0))


    entries = []

    # Interpolated color at threshold
    threshold_color = interpolate_color(threshold, COLORMAP_BLUE_BROWN)

    for q, color in COLORMAP_BLUE_BROWN:
        if q < threshold:
            entries.append(f'<ColorMapEntry color="{color}" quantity="{q}" opacity="0.0"/>')
    
    entries.append(f'<ColorMapEntry color="{threshold_color}" quantity="{threshold - 0.01}" opacity="0.0"/>')
    entries.append(f'<ColorMapEntry color="{threshold_color}" quantity="{threshold}" opacity="1.0"/>')

    for q, color in COLORMAP_BLUE_BROWN:
        if q > threshold:
            entries.append(f'<ColorMapEntry color="{color}" quantity="{q}" opacity="1.0"/>')


    colormap_xml = "\n".join(entries)

    sld = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <StyledLayerDescriptor 
        version="1.0.0"
        xmlns="http://www.opengis.net/sld"
        xmlns:sld="http://www.opengis.net/sld"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:gml="http://www.opengis.net/gml">

    <NamedLayer>
        <Name>spreewassern_raster:Entwaesserungswahrscheinlichkeit_9Parameter_v2</Name>
        <UserStyle>
        <Name>threshold_style</Name>

        <FeatureTypeStyle>
            <Rule>
            <RasterSymbolizer>
                <sld:ChannelSelection>
                    <sld:GrayChannel>
                        <sld:SourceChannelName>1</sld:SourceChannelName>
                    </sld:GrayChannel>
                </sld:ChannelSelection>
                <!-- ORIGINAL COLORMAP -->
                <ColorMap type="ramp">
                {colormap_xml}
                </ColorMap>

            </RasterSymbolizer>
            </Rule>
        </FeatureTypeStyle>

        </UserStyle>
    </NamedLayer>
    </StyledLayerDescriptor>

    """
    # keep only allowed params
    wms_params = {k: v for k, v in params.items() if k.lower() in ALLOWED_WMS_PARAMS}
    wms_params['SLD_BODY'] = sld
    response = requests.get(
        geoserver_url,
        params=wms_params,
    )

    return HttpResponse(
        response.content,
        content_type=response.headers.get("Content-Type")
    )


def load_sieker_drainage_gui(request, user_field_id):
    print('arrived in views')
    user = request.user
    if request.method == 'GET':
        toolbox_type = models.ToolboxType.objects.get(name_tag='drainage')
        user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='drainage')
        drainage_probabiliy_filter_form = forms.DrainageProbabilityFilterForm()

        # TODO check all objects.all()
        drained_areas = models.DrainedArea.objects.filter(geom4326__within=user_field.geom)
        drained_area_filter_form = filters.DrainedAreaFilter(queryset=drained_areas)

        
        drainage_network = models.DrainageNetwork.objects.filter(geom4326__within=user_field.geom)
        print('drainageNetwork COUNT', drainage_network.count())

        details = models.DrainageNetworkTypeDetail.objects.filter(drainagenetwork__in=drainage_network).distinct()
        drainage_network_filter_form = filters.DrainageNetworkFilter(queryset=details)

        detail_types = models.DrainageNetworkType.objects.filter(details__in=details).distinct()
        print('details COUNT', details.count(), detail_types)

           
        drainage_network_labels = { d.name_tag: d.name_de for d in detail_types }
        details_exist = detail_types.count() > 0

        
        labels_colors_details = models.DataInfo.objects.filter(data_type__in=details.values('name_tag'))
        labels_colors_areas = models.DataInfo.objects.filter(data_type__in=models.DrainedAreaType.objects.all().values('name_tag'))
        colors = {di.data_type: di.feature_color for di in labels_colors_details}
        colors.update({di.data_type: di.feature_color for di in labels_colors_areas})

        result_form = forms.SiekerDrainageDownloadForm()
        default_project = filters.create_default_project(
        user_field, 
        [
            drainage_probabiliy_filter_form, 
            drained_area_filter_form, 
            drainage_network_filter_form, 
            result_form,

        ],
        'drainage'
        )
        print(default_project)
        
        html = render_to_string('toolbox/sieker_drainage.html', {
            'project_select_form': project_select_form,
            'drainage_probabiliy_filter_form': drainage_probabiliy_filter_form,
            'drained_area_filter_form': drained_area_filter_form,
            'drainage_network_filter_form': drainage_network_filter_form,
            'labels': drainage_network_labels,
            'details_exist': details_exist,
            'result_form': result_form,
            
        }, request=request)
        
        return JsonResponse({
            'success': True, 
            'html': html, 
            'colors': colors,
            'default_project': default_project,
            })
       
def load_sieker_drainage_features(request, user_field_id):
    print('load_sieker_drainage_features')
    user = request.user
    if request.method == 'GET':
        user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))

        drained_areas = models.DrainedArea.objects.filter(geom4326__within=user_field.geom)
    
        drained_area_type_ids = list(drained_areas.values_list('drained_area_type__id', flat=True).distinct())
        drained_area_types = models.DrainedAreaType.objects.filter(pk__in=drained_area_type_ids)
        drainage_type_feature_collections = []
        for dt in drained_area_types:          
            drainage_type_feature_collections.append({
                'drainedAreaTypeId': dt.id,
                'dataInfo': models.DataInfo.objects.get(data_type=dt.name_tag).to_json(),
                'featureCollection': create_feature_collection(drained_areas.filter(drained_area_type__id=dt.id)),
                })


        drainage_network = models.DrainageNetwork.objects.filter(geom4326__within=user_field.geom)
        detail_ids = drainage_network.values_list('network_type_detail__id', flat=True).distinct()
        details = models.DrainageNetworkTypeDetail.objects.filter(pk__in=detail_ids)

        network_type_detail_feature_collections = []
        for detail in details:     
            network_type_detail_feature_collections.append({
                'drainageNetworkTypeId': detail.network_type.id,
                'drainageNetworkTye': detail.network_type.name_tag,
                'drainageNetworkTypeDetailId': detail.id,
                'dataInfo': models.DataInfo.objects.get(data_type=detail.name_tag).to_json(),
                'featureCollection': create_feature_collection(drainage_network.filter(network_type_detail=detail))
                })

        if details.count() > 0 or drained_area_types.count() > 0:
            return JsonResponse({
                'success': True, 
                'drainage_type_feature_collections': drainage_type_feature_collections,
                'network_type_detail_feature_collections': network_type_detail_feature_collections,
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Es gibt weder drainierte Flächen noch Enbtwässerungen im Suchgebiet.'
            })
def create_geojson_from_feature_collection(fc, tmpdir, filename):   
    file_path = os.path.join(tmpdir, filename)
    with open(f"{file_path}.geojson", "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2)

def create_shp_from_feature_collection(tmpdir, feature_collection, epsg, filename, writer_fields):
    
    shp_path = os.path.join(tmpdir, filename)

    writer = shapefile.Writer(shp_path)
    for key, val in writer_fields.items():
        writer.field(key[:10], val['field_type'], decimal=val['decimal'])
    for feature in feature_collection["features"]:
        geom = shapely_shape(feature["geometry"])
        props = feature["properties"]

        writer.shape(geom.__geo_interface__)


        record_values = [props.get(field) or 0 if writer_fields[field]['field_type'] in ('N', 'F') else props.get(field, '') 
                        for field in writer_fields]
        
        writer.record(*record_values) 

    writer.close()  
 

def check_for_point_results(download_list):
    point = False
    full = False
    for filetype in download_list:               
        if filetype.split('_')[0] == 'pt':
            point = True
        else:
            full = True
    return point, full

def create_fc_for_sink_download(project, sinks, epsg, sink_type, result_list, language='de'):

    
    
    
    indices = calculate_indices_df(sinks, project, sink_type=sink_type)
    pt_feature_collection = {}
    feature_collection = {}
    point, full = check_for_point_results(result_list)
    if point:

        pt_feature_collection = {
            "type": "FeatureCollection",
            "features": [obj.to_point_feature(indices, epsg=epsg, language=language) for obj in sinks],
            "crs": {
                "type": "name",
                "properties": {"name": f"EPSG:{epsg}"}
            }
        } 
    if full:
        feature_collection = {
                "type": "FeatureCollection",
                "features": [obj.to_feature(indices, epsg=epsg, language=language) for obj in sinks],
                "crs": {
                    "type": "name",
                    "properties": {"name": f"EPSG:{epsg}"}
                }
            }
        
    return {'feature_collection': feature_collection, 'pt_feature_collection': pt_feature_collection, 'filename': sinks.model.get_filename(language=language)}

    # for filetype in result_list: 
    #     filename = sinks.model.get_filename(language=language)
    #     if filetype.split('_')[0] == 'pt':
    #         fc = pt_feature_collection
    #         filename = filename + '_points'
    #     else:
    #         fc = feature_collection

    #     filename = f'{filename}_EPSG_{epsg}'

    #     if filetype.split('_')[-1] == 'shp':
    #         writer_fields = sinks.model.shp_writer_fields()
    #         create_shp_from_feature_collection(tmpdir, fc, epsg, filename, writer_fields)
    #     elif filetype.split('_')[-1] == 'gjson':
    #         create_geojson_from_feature_collection(fc, tmpdir, filename)


def create_fc_for_download(data, epsg, result_list, language='de'):
    """
    Docstring for create_download
    
    :param data: queryset of model instances
    :param epsg: EPSG code for coordinate reference system
    :param result_list: list of result download-file types
    :param language: language code for localization
    """


    
    pt_feature_collection = {}
    feature_collection = {}
    point, full = check_for_point_results(result_list)
    if point:

        pt_feature_collection = {
            "type": "FeatureCollection",
            "features": [obj.to_point_feature( epsg=epsg, language=language) for obj in data],
            "crs": {
                "type": "name",
                "properties": {"name": f"EPSG:{epsg}"}
            }
        } 
    if full:
        feature_collection = {
                "type": "FeatureCollection",
                "features": [obj.to_feature( epsg=epsg, language=language) for obj in data],
                "crs": {
                    "type": "name",
                    "properties": {"name": f"EPSG:{epsg}"}
                }
            }
        
    return {'feature_collection': feature_collection, 'pt_feature_collection': pt_feature_collection, 'filename': data.model.get_filename(language=language)}

def create_download_files(feature_collections, data, tmpdir, epsg, result_list, language='de'):
    """
    data : dictionary with pt_feature_collection and feature_collection
    tmpdir : temporary directory path
    """
    base_filename = feature_collections['filename']
    for filetype in result_list: 
        filename = copy(base_filename)
        if filetype.split('_')[0] == 'pt':
            fc = feature_collections['pt_feature_collection']
            filename = filename + '_points'
        else:
            fc = feature_collections['feature_collection']
            

        if filetype.split('_')[-1] == 'shp':
            writer_fields = data.model.shp_writer_fields()
            create_shp_from_feature_collection(tmpdir, fc, epsg, filename, writer_fields)
        elif filetype.split('_')[-1] == 'gjson':
            create_geojson_from_feature_collection(fc, tmpdir, filename)
        elif filetype == 'csv':
            file_path = os.path.join(tmpdir, f'{filename}.csv')
            dataset = [obj.to_json(language=language) for obj in data]
            rows = [row for row in dataset[0].keys()]
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(rows)
                
                for obj in dataset:
                    writer.writerow([obj[key] for key in rows])

def create_download_csv_from_feature_collection(feature_collection, tmpdir, filename, language='de'):   
    file_path = os.path.join(tmpdir, f'{filename}.csv')
    features = feature_collection.get('features', [])

    if len(features) == 0:
        return
    rows = [row for row in features[0]['properties'].keys()]
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(rows)
        
        for feature in features:
            props = feature['properties']
            writer.writerow([props.get(key, '') for key in rows])
                    



def download_toolbox_results(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        project = request.body
        print('Project:', type(project))
        project = json.loads(project)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid project JSON'}, status=400)
    


    language = 'de'
    
    project_type = project.get('toolboxType')
    epsg = int(project.get('result_crs', ['25833'])[0])
    tmpdir = tempfile.mkdtemp()

    
    match project_type:
        case 'infiltration':
            print('is Infiltration')
            
            result_result = project.get('result_result', [])
            result_sinks = project.get('result_sinks', [])
            result_enlarged_sinks = project.get('result_enlarged_sinks', [])
            result_waterbodies = project.get('result_waterbodies', [])
            result_timeseries = project.get('result_timeseries', [])
            
            if len(result_result) > 0:
                result = get_infiltration_result_list(project, epsg=epsg)
                fc = result.get('inlet_feature_collection')
                for filetype in result_result:
                    if filetype.split('_')[-1] == 'shp':
                        # writer_fields = data.model.shp_writer_fields()
                        writer_fields = {
                            'distance_m':{'field_type': "N", 'decimal': 0},
                            'index_length':{'field_type': "N", 'decimal': 0},
                            'index_volumes':{'field_type': "N", 'decimal': 0},
                            'index_inlet': {'field_type': "N", 'decimal': 0},
                        }
                        filename = f'Zuleitungen_EPSG_{epsg}'
                        create_shp_from_feature_collection(tmpdir, fc, epsg, filename, writer_fields)
                        if 'shp' not in result_sinks:
                            result_sinks.append('shp')
                        if 'shp' not in result_sinks:
                            result_sinks.append('shp')
                    elif filetype.split('_')[-1] == 'gjson':
                        create_geojson_from_feature_collection(fc, tmpdir, filename)
                        if 'gjson' not in result_sinks:
                            result_sinks.append('gjson')
                        if 'gjson' not in result_sinks:
                            result_sinks.append('gjson')


            if len(result_sinks) > 0:
                sinks = models.Sink.objects.filter(id__in=project.get(f'selected_sinks', []))
                sink_fc = create_fc_for_sink_download(project, sinks, epsg, 'sink', result_sinks, language=language)
                create_download_files(sink_fc, sinks, tmpdir, epsg, result_sinks, language=language)
            if len(result_enlarged_sinks) > 0:
                sinks = models.EnlargedSink.objects.filter(id__in=project.get(f'selected_enlarged_sinks', []))
                enlarged_sink_fc = create_fc_for_sink_download(project, sinks, epsg, 'enlarged_sink', result_enlarged_sinks, language=language)
                create_download_files(enlarged_sink_fc, sinks, tmpdir, epsg, result_enlarged_sinks, language=language)
                sink_embankments = models.SinkEmbankment.objects.filter(enlarged_sink__in=sinks)
                if sink_embankments.count() > 0:
                    embankment_fc = create_fc_for_download(sink_embankments, epsg, result_enlarged_sinks, language=language)
                    create_download_files(embankment_fc, sink_embankments, tmpdir, epsg, result_enlarged_sinks, language=language)
            
            if len(result_waterbodies) > 0:
                lakes = models.Lake.objects.filter(id__in=project.get(f'selected_lakes', []))
                streams = models.Stream.objects.filter(id__in=project.get(f'selected_streams', []))
                lakes_fc = create_fc_for_download(lakes, epsg, result_waterbodies, language=language)
                
                create_download_files(lakes_fc, lakes, tmpdir, epsg, result_waterbodies, language=language)
                streams_fc = create_fc_for_download(streams, epsg, result_waterbodies, language=language)
                
                create_download_files(streams_fc, streams, tmpdir, epsg, result_waterbodies, language=language)
                if len(result_timeseries) > 0:
                    fgw_ids = list(lakes.values_list('fgw_id', flat=True)) + \
                        list(streams.values_list('fgw_id', flat=True))
                    fgw_ids = set(fgw_ids)
                    fgw_ids = [x for x in fgw_ids if x is not None]
                    
                    for fgw_id in fgw_ids:

                        timeseries = (
                            models.DischargeTimeseries.objects
                                .filter(fgw__id=fgw_id)
                                .order_by('date')
                                .values('date', 'discharge_m3s')
                            )
                        filename = f'discharge_timeseries_fgw_id_{fgw_id}.csv'

                        file_path = os.path.join(tmpdir, filename)
                        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                            writer = csv.writer(csvfile)
                            
                            # Write header
                            writer.writerow(["date", "discharge_m3s"])
                            
                            # Write rows
                            for row in timeseries:
                                writer.writerow([row["date"], row["discharge_m3s"]])
                    
        case 'injection':
            filename= f'/app/raster_data/{request.user.id}_mar_result.tif'
            target_path = os.path.join(tmpdir, "mar_result.tif")
            # copy file into tmpdir
            shutil.copy(filename, target_path)
            
        case 'sieker_surface_water':
            result_lakes = project.get('result_lakes', [])
            result_stations = project.get('result_stations', [])
            result_timeseries = project.get('result_timeseries', [])
            if len(result_lakes) > 0:
                lake_ids = project.get('selected_sieker_surface_waters', [])
                lakes = models.SiekerLargeLake.objects.filter(id__in=lake_ids)
                lakes_fc = create_fc_for_download(lakes, epsg, result_lakes, language=language)
                create_download_files(lakes_fc, lakes, tmpdir, epsg, result_lakes, language=language)
                
            if len(result_stations) > 0:
                wl_ids = project.get('selected_sieker_water_levels', [])
                stations = models.SiekerWaterLevel.objects.filter(id__in=wl_ids)
                stations_fc = create_fc_for_download(stations, epsg, result_stations, language=language)
                create_download_files(stations_fc, stations, tmpdir, epsg, result_stations, language=language)

            if len(result_timeseries) > 0:
                wl_ids = project.get('selected_sieker_water_levels', [])
                stations = models.SiekerWaterLevel.objects.filter(id__in=wl_ids)
                for station in stations:

                    timeseries = (
                        models.TimeseriesDailyWaterlevel.objects
                        .filter(station__id=station.station.id)
                        .order_by('date')
                        .values('date', 'level')
                    )
                    filename = f'{(station.name.replace(" ", "_")).replace(",", "")}_timeseries.csv'
                    file_path = os.path.join(tmpdir, filename)
                    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # Write header
                        writer.writerow(["date", "level"])
                        
                        # Write rows
                        for row in timeseries:
                            writer.writerow([row["date"], row["level"]])
            
        case 'sieker_sink':
            result_result = project.get('result_result', [])
            result_sinks = project.get('result_sinks', [])
            result_waterbodies = project.get('result_waterbodies', [])
            result_timeseries = project.get('result_timeseries', [])
            
            if len(result_result) > 0:
            
                sinks = models.SiekerSink.objects.filter(id__in=project.get(f'selected_sieker_sinks', []))
                lakes = models.Lake.objects.filter(id__in=project.get(f'selected_sieker_lakes', []))
                streams = models.Stream.objects.filter(id__in=project.get(f'selected_sieker_streams', []))

                result = get_sieker_sink_result_list(sinks, lakes, streams, epsg=epsg)
                inlet_fc = result.get('inlet_feature_collection')
                sink_fc = result.get('sink_feature_collection')
                for filetype in result_result:
                    if filetype.split('_')[-1] == 'shp':
                        # writer_fields = data.model.shp_writer_fields()
                        writer_fields = {
                            'distance_m':{'field_type': "N", 'decimal': 0},
                            'index_length':{'field_type': "N", 'decimal': 0},
                            'index_volumes':{'field_type': "N", 'decimal': 0},
                        }
                        filename = f'Zuleitungen_EPSG_{epsg}'
                        create_shp_from_feature_collection(tmpdir, inlet_fc, epsg, filename, writer_fields)
                        
                        if 'shp' not in result_sinks:
                            result_sinks.append('shp')

                    elif filetype.split('_')[-1] == 'gjson':
                        create_geojson_from_feature_collection(inlet_fc, tmpdir, filename)
                        if 'gjson' not in result_sinks:
                            result_sinks.append('gjson')

            if len(result_sinks) > 0:
                sinks = models.Sink.objects.filter(id__in=project.get(f'selected_sinks', []))

                sink_fc = create_fc_for_download(sinks, epsg, result_sinks, language=language)
                create_download_files(sink_fc, sinks, tmpdir, epsg, result_sinks, language=language)

            if len(result_waterbodies) > 0:
                lakes = models.Lake.objects.filter(id__in=project.get(f'selected_lakes', []))
                streams = models.Stream.objects.filter(id__in=project.get(f'selected_streams', []))
                lakes_fc = create_fc_for_download(lakes, epsg, result_waterbodies, language=language)
                create_download_files(lakes_fc, lakes, tmpdir, epsg, result_waterbodies, language=language)
                streams_fc = create_fc_for_download(streams, epsg, result_waterbodies, language=language)
                create_download_files(streams_fc, streams, tmpdir, epsg, result_waterbodies, language=language)
            if len(result_timeseries) > 0:
                fgw_ids = list(lakes.values_list('fgw_id', flat=True)) + \
                    list(streams.values_list('fgw_id', flat=True))
                fgw_ids = set(fgw_ids)
                fgw_ids = [x for x in fgw_ids if x is not None]
                
                for fgw_id in fgw_ids:

                    timeseries = (
                        models.DischargeTimeseries.objects
                            .filter(fgw__id=fgw_id)
                            .order_by('date')
                            .values('date', 'discharge_m3s')
                        )
                    filename = f'discharge_timeseries_fgw_id_{fgw_id}.csv'

                    file_path = os.path.join(tmpdir, filename)
                    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # Write header
                        writer.writerow(["date", "discharge_m3s"])
                        
                        # Write rows
                        for row in timeseries:
                            writer.writerow([row["date"], row["discharge_m3s"]])

        case 'wetland':
            result_wetlands = project.get('result_wetlands', [])
            result_waterbodies = project.get('result_waterbodies', [])

            if len(result_wetlands) > 0:
                wetland_ids = project.get('selected_wetlands', [])
                wetlands = models.HistoricalWetlands.objects.filter(id__in=wetland_ids)
                wetland_fc = create_fc_for_download(wetlands, epsg, result_wetlands, language=language)
                create_download_files(wetland_fc, wetlands, tmpdir, epsg, result_wetlands, language=language)

            if len(result_waterbodies) > 0:
                stream_ids = project.get('selected_wetland_streams', [])
                streams = models.Stream.objects.filter(id__in=stream_ids)
                streams_fc = create_fc_for_download(streams, epsg, result_waterbodies, language=language)
                create_download_files(streams_fc, streams, tmpdir, epsg, result_waterbodies, language=language)

                lake_ids = project.get('selected_wetland_lakes', [])
                lakes = models.Lake.objects.filter(id__in=lake_ids)
                lakes_fc = create_fc_for_download(lakes, epsg, result_waterbodies, language=language)
                create_download_files(lakes_fc, lakes, tmpdir, epsg, result_waterbodies, language=language)

        case 'drainage':
            user_field_id = project.get('userField')
            user_field = models.UserField.objects.get(pk=user_field_id)
            result_drainage_network = project.get('result_drainage_network', [])
            result_drained_areas = project.get('result_drained_areas', []) 
            result_probability_raster = project.get('result_probability_raster', [])
            
            if len(result_drainage_network) > 0:
                drainage_network = models.DrainageNetwork.objects.filter(
                    Q(geom4326__within=user_field.geom) |
                    Q(geom4326__intersects=user_field.geom)
                )
                drainage_network_fc = create_fc_for_download(drainage_network, epsg, result_drainage_network, language=language)
                create_download_files(drainage_network_fc, drainage_network, tmpdir, epsg, result_drainage_network, language=language)

            if len(result_drained_areas) > 0:
                drained_area = models.DrainedArea.objects.filter(
                    Q(geom4326__within=user_field.geom) |
                    Q(geom4326__intersects=user_field.geom)
                )
                drained_area_fc = create_fc_for_download(drained_area, epsg, result_drained_areas, language=language)
                create_download_files(drained_area_fc, drained_area, tmpdir, epsg, result_drained_areas, language=language)
            if len(result_probability_raster)> 0:
                filename= f'/app/raster_data/Entwaesserungswahrscheinlichkeit_9Parameter_v2.tif'
                target_path = os.path.join(tmpdir, "Entwaesserungswahrscheinlichkeit.tif")
                # copy file into tmpdir
                shutil.copy(filename, target_path)

        case 'sieker_gek':
            result_geks = project.get('result_geks', [])
            result_measures = project.get('result_measures', [])

            geks, measures = get_geks_and_measures(project)
            gek_measures_features=[]

            for m in measures:
                ft = m.gek_retention.to_feature( epsg=epsg, language=language)
                m_dict = m.to_json(language=language)
                m_dict['measure_id'] = m_dict.pop('id')
                ft['properties'].update(m_dict)
                gek_measures_features.append(ft)

            measures_fc = {
                "type": "FeatureCollection",
                "features": gek_measures_features,
                "crs": {
                    "type": "name",
                    "properties": {"name": f"EPSG:{epsg}"}
                }
            }

            
            filename = f'Sieker_GEKs_EPSG_{epsg}'
            geks_fc = create_fc_for_download(geks, epsg, result_geks, language=language)
            create_download_files(geks_fc, geks, tmpdir, epsg, result_geks, language=language) 
            if 'csv' in result_measures:
                result_measures.remove('csv')
                create_download_csv_from_feature_collection(measures_fc, tmpdir, 'Gewaesserentwicklungsmassnahmen', language=language)


            create_download_files({
                'feature_collection': measures_fc,
                'filename': 'Gewaesserentwicklungsmassnahmen',
                }, measures, tmpdir, epsg, result_measures, language=language)
        
        




    #### zip and return
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(tmpdir):
            for f in files:
                file_path = os.path.join(root, f)
                arcname = os.path.relpath(file_path, tmpdir)  # keep relative paths
                zf.write(file_path, arcname)
                

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="results.zip"'
    return response




