from django.shortcuts import render
from swn import models as swn_models
from swn import forms as swn_forms
from swn.views import load_nuts_polygon
from . import forms, models

from .filters import SiekerLargeLakeFilter,  SinkFilter, EnlargedSinkFilter, StreamFilter, LakeFilter, SiekerSinkFilter, GekRetentionFilter, HistoricalWetlandsFilter
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry, LineString
from django.contrib.gis.measure import D
from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.forms.models import model_to_dict

from django.template.loader import render_to_string
from django.db import connection
from django.db.models import Max, Min, F, Q
import json, requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

from shapely.geometry import shape as shapely_shape, mapping
from shapely.ops import nearest_points, transform
from pyproj import Transformer
from collections import defaultdict
import pandas as pd

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform, transform_geom
from rasterio.mask import mask
from rasterio.enums import ColorInterp



transformer_25833_to_4326 = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)







def publish_raster_geoserver(tif_path, layer_name, workspace, style_name="style_raster_percent"):
    """
    Publishes a GeoTIFF to GeoServer as a coverage store and layer.
    """
    x_path = 'raster_data/' + layer_name + '.tif'
    workspace = "spreewassern_raster"
    store_name = layer_name  # one store per raster
    headers = {"Content-type": "image/tiff"}

    # 1. Upload GeoTIFF to a new coverage store
    url = f"{settings.GEOSERVER_USER}/workspaces/{workspace}/coveragestores/{store_name}/file.geotiff"

    with open(tif_path, "rb") as f:
        r = requests.put(
            url,
            data=f,
            headers=headers,
            auth=HTTPBasicAuth(settings.GEOSERVER_USER, settings.GEOSERVER_PASS)
        )
    r.raise_for_status()

    layer_url = f"{settings.GEOSERVER_URL}/layers/{workspace}:{layer_name}"
    r = requests.put(
        layer_url,
        headers={"Content-type": "application/xml"},
        data=f"<layer><defaultStyle><name>{style_name}</name></defaultStyle></layer>",
        auth=HTTPBasicAuth(settings.GEOSERVER_USER, settings.GEOSERVER_PASS)
    )
    r.raise_for_status()


def create_feature_collection(queryset):
    return {
        "type": "FeatureCollection",
        "features": [obj.to_feature() for obj in queryset],
    }


def create_point_feature_collection(queryset):
    return  {
        "type": "FeatureCollection",
        "features": [obj.to_point_feature() for obj in queryset],
        }



# # TOOLBOX GENERAL
# def create_default_project(user):
#     """
#     Create a default project for the user.
#     """
#     default_project = models.ToolboxProject(
#         name= '',
#         user=user,
#     ).to_json()

#     return json.dumps(default_project, default=str)


def toolbox_dashboard(request):
    user = request.user
    project_region = swn_models.ProjectRegion.objects.first().to_feature()

    outline_injection = models.OutlineInjection.objects.first().to_feature()

    outline_surface_water = models.OutlineSurfaceWater.objects.first().to_feature()

    outline_infiltration = models.OutlineInfiltration.objects.first().to_feature()


    state_county_district_form = swn_forms.PolygonSelectionForm(request.POST or None)
    # project_select_form = forms.ToolboxProjectSelectionForm(user=user)
    # project_select_form = forms.ToolboxProjectSelectionForm()
    project_form = forms.ToolboxProjectForm(user=user)
    project_modal_title = 'Create new project'

    # default_project = create_default_project(user)

    context = {
        'project_region': project_region,
        # 'default_project': default_project,
        'state_county_district_form': state_county_district_form,
        # 'project_select_form': project_select_form,
        'project_form': project_form,
        'project_modal_title': project_modal_title,
        'outline_injection': outline_injection,
        'outline_surface_water': outline_surface_water,
        'outline_infiltration': outline_infiltration,
        # 'all_lakes_feature_collection': all_lakes_feature_collection,
        # 'all_rivers_feature_collection': all_rivers_feature_collection,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)


def save_toolbox_project(request):
    if request.method != 'POST':
        return JsonResponse({'message': {'success': False, 'message': 'Invalid request method'}}, status=405)

    try:
        user = request.user
        request_data = json.loads(request.body)

        toolbox_type = models.ToolboxType.objects.get(name_tag=request_data['toolboxType'])
        user_field = models.UserField.objects.get(pk=request_data['userField'])
        print('iserField None?', user_field)

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

                message = f'Project {project.name} updated'
                status = 200

            except models.ToolboxProject.DoesNotExist:
                return JsonResponse({'message': {'success': False, 'message': 'Project not found'}}, status=404)

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
            message = f'Project {project.name} created'
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
        return JsonResponse({'success': False, 'message': 'Project not found'})
    else:
        project_json = project.to_json()
        return JsonResponse({'success': True, 'message': f'Project {project.name} loaded', 'project': project_json})

    

@login_required
@csrf_protect
def save_user_field(request):
    print('Request:', request, request.user, request.method, request.body)
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
        ufs = []
        for user_field in user_fields:
            uf = user_field.to_feature()
            uf['properties']['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
        # print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})


@login_required
# @csrf_protect
def delete_user_field(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            user_field = models.UserField.objects.get(id=id)

            if user_field.user == request.user:
                user_field.delete()
                return JsonResponse({'message': {'success': True, 'message': 'Field deleted'}})
            else:
                return JsonResponse({'message': {'success': False, 'message': 'You do not have permission to delete this field'}}, status=403)

        except models.UserField.DoesNotExist:
            return JsonResponse({'message': {'success': False, 'message': 'Field not found'}}, status=404)
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Invalid request'}}, status=400)
    
@login_required
def get_field_project_modal(request, id):
    user_projects = models.ToolboxProject.objects.filter(Q(user_field__id=id) & Q(user_field__user=request.user)).order_by('name')

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
        user_field_id = None
    else:
        user_field_id = int(user_field_id)

    start_load_projects = datetime.now()
    toolbox_type = models.ToolboxType.objects.get(name_tag='infiltration')
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    qs = models.ToolboxProject.objects.filter(
        Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
    ).order_by('-creation_date').reverse()
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
    print("Time to load projects:", datetime.now() - start_load_projects)
    
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    start_filter_sinks = datetime.now()
    # TODO these querysets are not necessary if the has_x attributes are implemented
    sinks = models.Sink.objects.filter(centroid__within=user_field.geom)    
    
    print("Time to filter sinks:", datetime.now() - start_filter_sinks)

    start_sink_loop = datetime.now()
    if user_field.has_infiltration:
        sinks = models.Sink.objects.filter(centroid__within=user_field.geom)
        enlarged_sinks = models.EnlargedSink.objects.filter(centroid__within=user_field.geom)
        streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))
        lakes = models.Lake.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        if user_field.filter_bounds.get('sinks') is None:
            print('FOUND Sinks no bounds')
            user_field.compute_filter_bounds_infiltration()

        print("Time to loop stream and lake filter:", datetime.now() - start_sink_loop)
        lake_form = LakeFilter(
            request.GET,
            queryset=lakes,
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
        )
        stream_form = StreamFilter(
            request.GET,
            queryset=streams,
            bounds=user_field.filter_bounds.get('streams') if user_field.filter_bounds else None
        )
        sink_form = SinkFilter(
            request.GET,
            queryset=sinks,
            bounds=user_field.filter_bounds.get('sinks') if user_field.filter_bounds else None
        )
        print("Queryset Sinks", sinks.count())
        enlarged_sink_form = EnlargedSinkFilter(
            request.GET,
            queryset=enlarged_sinks,
            bounds=user_field.filter_bounds.get('enlarged_sinks') if user_field.filter_bounds else None
        )
        print("Time to loop end:", datetime.now() - start_sink_loop)


        overall_weighting = forms.OverallWeightingsForm()
        forest_weighting = forms.WeightingsForestForm()
        agriculture_weighting = forms.WeightingsAgricultureForm()
        grassland_weighting = forms.WeightingsGrasslandForm()


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
        }, request=request) 

        
        return JsonResponse({'success': True, 'html': html})
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
    return sink_indices


def filter_sinks(request):

    start = datetime.now()
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    
    geom = GEOSGeometry(user_field.geom)
    
    sinks = models.Sink.objects.filter(geom4326__within=geom)
    print("Sinks:", sinks.count())
    filters = Q()
    filters = add_range_filter(filters, project, 'sink_area', 'area')
    filters = add_range_filter(filters, project, 'sink_volume', 'volume')
    filters = add_range_filter(filters, project, 'sink_depth', 'depth')
    # filters = add_range_filter(filters, project, 'sink_index_soil', 'index_soil')
    sinks = sinks.filter(filters)
    print("Sinks FILTERED:", sinks.count())

    land_use_values = project.get('sink_land_use', [])
    land_use_values = [int(value) for value in land_use_values if value.isdigit()]
    land_use_filter = (
        Q(landuse_1__in=land_use_values) &
        (Q(landuse_2__in=land_use_values) |
        Q(landuse_2__isnull=True)) &
        (Q(landuse_3__in=land_use_values) |
        Q(landuse_3__isnull=True))
        )
    # sinks = sinks.filter(land_use_filter)
    print("Sinks LAND USE FILTERED:", sinks.count())
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        print("Sinks", sinks.count())
        
        sink_indices_soil = calculate_indices_df(sinks, project, sink_type='sink')

        features = []
        for sink in sinks:
            # centroid = sink.centroid
            geojson = sink.to_point_feature(language='de')

            sink_id = sink.id
            index_soil = sink_indices_soil.get(sink_id, 0)

            if sink.index_hydrogeology:
                index_sink_total = round(
                    (index_soil + sink.index_proportions + sink.index_feasibility  + sink.index_hydrogeology) / .04)  
            else:       
                index_sink_total = round(
                    (index_soil + sink.index_proportions + sink.index_feasibility ) / .03) 
            print('geojson:', geojson)
            geojson['properties']["index_sink_total"] = index_sink_total/100
            geojson['properties']["index_sink_total_str"] = index_sink_total

            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} sinks'
        }

        data_info = models.DataInfo.objects.get(data_type='sink').to_dict()

        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    

def filter_enlarged_sinks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    sinks = models.EnlargedSink.objects.filter(geom4326__within=geom)

    filters = Q()
    filters = add_range_filter(filters, project, 'enlarged_sink_area', 'area')
    filters = add_range_filter(filters, project, 'enlarged_sink_volume', 'volume')
    filters = add_range_filter(filters, project, 'enlarged_sink_depth', 'depth')
    filters = add_range_filter(filters, project, 'enlarged_sink_volume_construction_barrier', 'volume_construction_barrier')
    filters = add_range_filter(filters, project, 'enlarged_sink_volume_gained', 'volume_gained')
    # filters = add_range_filter(filters, project, 'enlarged_sink_index_soil', 'index_soil')
    sinks = sinks.filter(filters)
    print('Enlarged_sinks 1', sinks)

    land_use_values = project.get('enlarged_sink_land_use', [])
    land_use_values = [int(value) for value in land_use_values if value.isdigit()]
    land_use_filter = (
        Q(landuse_1__in=land_use_values) &
        (Q(landuse_2__in=land_use_values) |
        Q(landuse_2__isnull=True)) &
        (Q(landuse_3__in=land_use_values) |
        Q(landuse_3__isnull=True))&
        (Q(landuse_4__in=land_use_values) |
        Q(landuse_4__isnull=True))
        )
    sinks = sinks.filter(land_use_filter)

    features = []
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        sink_indices_soil = calculate_indices_df(sinks, project, sink_type='enlarged_sink')
        for sink in sinks:
            
            geojson = sink.to_point_feature(language='de')
            sink_id = sink.id
            index_soil = sink_indices_soil.get(sink_id, 0)

            if sink.index_hydrogeology:
                index_sink_total = round(
                    (index_soil + sink.index_proportions + sink.index_feasibility  + sink.index_hydrogeology) / .04)  
            else:       
                index_sink_total = round(
                    (index_soil + sink.index_proportions + sink.index_feasibility ) / .03) 
            print('geojson:', geojson)
            geojson['properties']["index_sink_total"] = index_sink_total/100
            geojson['properties']["index_sink_total_str"] = f'{index_sink_total}'
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} Enlarged sinks'
        }

        data_info = models.DataInfo.objects.get(data_type='enlarged_sink').to_dict()

        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})

def filter_waterbodies(request):

    try:
        request = json.loads(request.body)
        project = request['project']
        data_type = request['dataType']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if data_type == 'lake':
        waterbody_class = models.Lake
    elif data_type == 'stream':
        waterbody_class = models.Stream

    data_info = models.DataInfo.objects.get(data_type=data_type).to_dict()

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)

    distance = int(project.get('lake_distance_to_userfield', 0))
    lakes = None
    if distance > 0:
        # Transform to EPSG:25833 (meters) and add the buffer
        user_geom_25833 = user_field.geom.transform(25833, clone=True)
        buffer_25833 = user_geom_25833.buffer(distance)
        buffer_4326 = buffer_25833.transform(4326, clone=True)
        lakes = waterbody_class.objects.filter(Q(geom__intersects=buffer_4326) | Q(geom__within=buffer_4326))
    else:
        lakes = waterbody_class.objects.filter(Q(geom__intersects=geom) | Q(geom__within=geom))

    filter = Q()
    filter = add_range_filter(filter, project, f'{data_type}_min_surplus', 'min_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_mean_surplus', 'mean_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_max_surplus', 'max_surplus_volume')
    filter = add_range_filter(filter, project, f'{data_type}_plus_days', 'plus_days')
    lakes = lakes.filter(filter)

    if lakes.count() == 0:
        message = {
            'success': False, 
            'message': f'No lakes found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No lakes found.'}})
    else:
        
        feature_collection = create_feature_collection(lakes)
        message = {
            'success': True, 
            'message': f'Found {lakes.count()} lakes'
        }
        print('feature_collection:', feature_collection)
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
        

def get_weighting_forms(request):
    if request.method == 'POST':
        project = json.loads(request.body)
        print('Project:', project)
        sinks = project.get('selected_sinks', [])
        enlarged_sinks = project.get('selected_enlarged_sinks', [])
        
        land_use_values = {}
        if len(sinks) > 0:
            sinks = [int(sink) for sink in sinks]
            queryset = models.Sink.objects.filter(id__in=sinks)
            land_use_values = set(
                queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
            ).union(
                queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
            ).union(
                queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
            )
        if len(enlarged_sinks) > 0:
            enlarged_sinks = [int(sink) for sink in enlarged_sinks]
            queryset = models.EnlargedSink.objects.filter(id__in=sinks)
            land_use_values.union(set(
                    queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
                ).union(
                    queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
                ).union(
                    queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
                ).union(
                    queryset.exclude(land_use_4__isnull=True).values_list('land_use_4', flat=True)
                )
            )
        
        land_use_values = list(land_use_values)

        context = {
            'forest_weighting': forms.WeightingsForestForm(),
            'agriculture_weighting': forms.WeightingsAgricultureForm(),
            'grassland_weighting': forms.WeightingsGrasslandForm(),
            'forms': {
                'grassland': False,
                'forest': False,
                'agriculture': False,
            }
        }
        # TODO weighting forms

        if 'forest_conifers' in land_use_values or 'forest_deciduous_trees' in land_use_values \
            or 'forest_conifers_and_deciduous_trees' in land_use_values:
            context['forms']['forest'] = True
        if 'agricultural_area_without_information' in land_use_values or 'farmland' in land_use_values:
            context['forms']['agriculture'] = True
        if 'grassland' in land_use_values:
            context['forms']['grassland'] = True
        

        return render(request, 'toolbox/weighting_tab.html', context)


def get_shortest_connection_lines_utm(sinks, lakes, streams):
    """
    Get the shortest connection line between the sinks and the nearest selected lake or stream.
    Returns a list of dictionaries with sink_id, waterbody_type, waterbody_id, line (WKT), and length_m.
    """
    results = []
    wos = []
    if sinks != [] and (lakes != [] or streams != []):
        for sink in sinks:
            sink_geom = shapely_shape(json.loads(sink.geom25833.geojson))

            min_dist = float('inf')
            closest_geom = None
            waterbody_type = None
            waterbody_id = None

            # Check lakes
            for lake in lakes:
                lake_geom = shapely_shape(json.loads(lake.geom25833.geojson))
                dist = sink_geom.distance(lake_geom)
                if dist < min_dist:
                    min_dist = dist
                    closest_geom = lake_geom
                    waterbody_type = 'lake'
                    waterbody_name = lake.name
                    waterbody_id = lake.id

            # Check streams
            for stream in streams:
                stream_geom = shapely_shape(json.loads(stream.geom25833.geojson))
                dist = sink_geom.distance(stream_geom)
                if dist < min_dist:
                    min_dist = dist
                    closest_geom = stream_geom
                    waterbody_type = 'stream'
                    waterbody_name = stream.name
                    waterbody_id = stream.id

            # Find nearest points and build LineString in EPSG:25833
            nearest = nearest_points(sink_geom, closest_geom)
            line = LineString([nearest[0].coords[0], nearest[1].coords[0]])
            line_geom = GEOSGeometry(line.wkt, srid=25833)
            line_geom.transform(4326)
            length_m = line.length  # Already in meters (EPSG:25833 is a projected CRS)

            if length_m >= 2000:
                rating_length = 0
            elif length_m >= 1000:
                rating_length = 5
            else:
                rating_length = int((1000 - length_m)/10)

            is_enlarged_sink = isinstance(sink, models.EnlargedSink)
            result = {
                'sink_id': sink.id,
                'sink_geom': json.loads(sink.geom4326.geojson),
                'is_enlarged_sink': is_enlarged_sink,
                'waterbody_type': waterbody_type,
                'waterbody_id': waterbody_id,
                'waterbody_name': waterbody_name,
                'line': json.loads(line_geom.geojson),
                'length_m': round(length_m, 2),
                'rating_connection': rating_length,
                'index_total': rating_length
            }

            wo = {
                'sink_id': sink.id,                
                'is_enlarged_sink': is_enlarged_sink,
                'waterbody_type': waterbody_type,
                'waterbody_id': waterbody_id,
                'waterbody_name': waterbody_name,
                'length_m': round(length_m, 2),
                'rating_connection': rating_length,
                'index_total': rating_length
            }
            if is_enlarged_sink:
                if sink.sink_embankment.first():
                    sink_embankment = sink.sink_embankment.first()
                    result['sink_embankment'] = sink_embankment.to_feature()
                

            results.append(result)
            wos.append(wo)
            
    with open('debug_lines.json', 'w') as f:
        json.dump(wos, f, indent=2)

    return results


def get_infiltration_results(request):
    # POST request
    project = json.loads(request.body)
    print('Project:', project)

    sinks = models.Sink.objects.filter(id__in=project.get('selected_sinks', []))
    enlarged_sinks = models.EnlargedSink.objects.filter(id__in=project.get('selected_enlarged_sinks', []))
    lakes = models.Lake.objects.filter(id__in=project.get('selected_lakes', []))
    streams = models.Stream.objects.filter(id__in=project.get('selected_streams', []))

    inlets_sinks = get_shortest_connection_lines_utm(sinks, lakes, streams)
    inlets_enlarged_sinks = get_shortest_connection_lines_utm(enlarged_sinks, lakes, streams)

    
    response = {
        'inlets_sinks': inlets_sinks + inlets_enlarged_sinks,
        'message': {
            'success': True,
            'message': f'Found {len(inlets_sinks)} pipes for sinks and {len(inlets_enlarged_sinks)} pipes for enlarged sinks.'
        }
    }
    print(response)
    return JsonResponse(response)


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
def sieker_surface_waters_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)

    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    lakes = models.SiekerLargeLake.objects.filter(Q(geom4326__within=user_field.geom) | Q(geom4326__intersects=user_field.geom))

    if lakes.count() > 0:
        toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_surface_water')
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
        sieker_lake_filter = SiekerLargeLakeFilter(
            request.GET,
            queryset=lakes,
            bounds=user_field.filter_bounds.get('lakes') if user_field.filter_bounds else None
            )

        water_levels = models.SiekerWaterLevel.objects.filter(
            geom4326__within=user_field.geom
        )
        lakes_feature_collection = create_feature_collection(lakes)
        water_levels_feature_collection = create_feature_collection(water_levels)

        lakes_data_info = models.DataInfo.objects.get(data_type='sieker_surface_water').to_dict()
        water_levels_data_info = models.DataInfo.objects.get(data_type='sieker_water_level').to_dict()


        layers = {
            'lakes': {
                'featureCollection':lakes_feature_collection,
                'dataInfo': lakes_data_info
            },
            'water_levels': {
                'featureCollection': water_levels_feature_collection,
                'dataInfo': water_levels_data_info
                }
            }
        

        html = render_to_string('toolbox/sieker_surface_waters.html', {
            'project_select_form': project_select_form,
            'sieker_lake_filter': sieker_lake_filter,      
        }, request=request) 

        return JsonResponse({'success': True, 'layers': layers , 'html': html})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet befinden sich keine geeigneten Seen.'})

    
## Sieker Oberflächengewässer / Large Lakes / Surface Waters
def filter_sieker_surface_waters(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)

    distance = int(project.get('lake_distance_to_userfield', 0))
    lakes = None
    if distance > 0:
        # Transform to EPSG:25833 (meters) and add the buffer
        user_geom_25833 = user_field.geom.transform(25833, clone=True)
        buffer_25833 = user_geom_25833.buffer(distance)
        buffer_4326 = buffer_25833.transform(4326, clone=True)
        lakes = models.SiekerLargeLake.objects.filter(Q(geom__intersects=buffer_4326) | Q(geom__within=buffer_4326))
    else:
        lakes = models.SiekerLargeLake.objects.filter(Q(geom__intersects=geom) | Q(geom__within=geom))

    filter = Q()
    filter = add_range_filter(filter, project, 'lake_volume', 'area_ha')
    filter = add_range_filter(filter, project, 'lake_volume', 'vol_mio_m3')
    filter = add_range_filter(filter, project, 'lake_max_depth', 'd_max_m')
    lakes = lakes.filter(filter)


    print("COUNT(Lakes)", lakes.count())

    if lakes.count() == 0:
        message = {
            'success': False, 
            'message': f'No lakes found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No lakes found.'}})
    else:
        
        feature_collection = create_feature_collection(lakes)
        message = {
            'success': True, 
            'message': 'Keine Seen im Suchgebiet entsprechen den Filterkriterien.'
        }
        print('feature_collection:', feature_collection)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})
        

##### Sieker Sinks ######
   
def load_sieker_sink_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)
    toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_sink')
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})

    qs = models.ToolboxProject.objects.filter(
        Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
    
    sinks = models.SiekerSink.objects.filter(
        centroid__within=user_field.geom
    )

    if sinks.count() > 0:
        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        sieker_sink_filter = SiekerSinkFilter(
            request.GET, 
            queryset=sinks,
            bounds=user_field.filter_bounds.get('sieker_sinks') if user_field.filter_bounds else None
            )

        html = render_to_string('toolbox/sieker_sink.html', {
            'project_select_form': project_select_form,
            'sieker_sink_filter': sieker_sink_filter,
        }, request=request) 

        return JsonResponse({'success': True, 'html': html})
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
    print("Sinks before filtering:", sinks.count())
    filters = Q()
    filters = add_range_filter(filters, project, 'sieker_sink_area', 'area')
    filters = add_range_filter(filters, project, 'sieker_sink_volume', 'volume')
    filters = add_range_filter(filters, project, 'sieker_sink_avg_depth', 'avg_depth')
    filters = add_range_filter(filters, project, 'sieker_sink_depth', 'depth')
    filters = add_range_filter(filters, project, 'sieker_sink_urbanarea_percent', 'urbanarea_percent')
    filters = add_range_filter(filters, project, 'sieker_sink_wetlands_percent', 'wetlands_percent')
    
    sinks = sinks.filter(filters)
    print("Sinks FILTERED:", sinks.count())

    feasibility = project.get('sieker_sink_feasibility', [])
    print('feasibility', feasibility)

    sinks = sinks.filter(Q(umsetzbark__in=feasibility))
    print("Sieker Sinks feasibility FILTERED:", sinks.count())
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        print("Sinks", sinks.count())
        
        data_info = models.DataInfo.objects.get(data_type='sieker_sink').to_dict()
        feature_collection = create_point_feature_collection(sinks)
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} sinks'
        }
        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    
   
def load_sieker_gek_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})


    geks = models.GekRetention.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    # all_sieker_gek_ids = [g.id for g in geks]
   

    if geks.count() > 0:
        toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_gek')
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)

        feature_collection = create_feature_collection(geks)

        gek_filter_form = GekRetentionFilter(
            request.GET, 
            queryset=geks,
            bounds=user_field.filter_bounds.get('sieker_geks') if user_field.filter_bounds else None
            )
        slider_labels = dict(models.GekPriority.objects.values_list("priority_level", "description_de").distinct().order_by("priority_level"))

        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        # sieker_geks_filter = SiekerGekFilter(request.GET, queryset=geks)

        html = render_to_string('toolbox/sieker_gek.html', {
            'project_select_form': project_select_form,
            'gek_filter_form': gek_filter_form  ,
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_dict()

        return JsonResponse({'success': True, 'html': html, 'featureCollection': feature_collection, 'slider_labels': slider_labels, 'dataInfo': data_info})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet sind keine Gewässerentwicklungskonzepte verfügbar.'})



# TODO: turn into filter gek
def filter_sieker_geks(request):
   # add_range_filter(filters, obj, field,  model_field=None)
    start = datetime.now()
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    print('FROM filter_sieker_geks project', project)
    
    # geks = models.GekRetention.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    # filter landuses
    ids = project.get('selected_sieker_geks')
    geks = models.GekRetention.objects.filter(pk__in=ids)
    landuses = models.GekLanduse.objects.filter(Q(gek_retention__in=geks) & Q(clc_landuse__id__in=project['gek_landuse']))
    geks = models.GekRetention.objects.filter(landuses__in=landuses).distinct()
    print("Geks:", geks.count())

    # filter measures
    filters = Q(priority__priority_level__gte=project['gek_priority'])
    filters = add_range_filter(filters, project, 'gek_costs', 'costs') 

    measures = models.GekRetentionMeasure.objects.filter(
            gek_retention__in=geks
        ).filter(filters)
    
    geks = models.GekRetention.objects.filter(measures__in=measures).distinct()


    print("Geks FILTERED:", geks.count())


    if geks.count() == 0:
        message = {
            'success': False, 
            'message': f'Es sind keine Gewässerentwicklungskonzepte für diese Filtereinstellungen bekannt.'
        }
        return JsonResponse({'message': message})
    else:
        print("Geks", geks.count())
        
        feature_collection = create_feature_collection(geks)
        data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_dict()
        data_info['featureColor'] = 'var(--bs-success)'

        dict_list = []
        for gek in geks:
            d = gek.to_dict()
            d['measures'] = [m.to_dict() for m in measures if m.gek_retention == gek]
            dict_list.append(d)
            
        print('measures: ', dict_list)

        data_info = models.DataInfo.objects.get(data_type='filtered_sieker_gek').to_dict()
        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'featureCollection': feature_collection, 'message' : {'success': True}, 'dataInfo': data_info, 'measures': dict_list})


# Sieker Wetlands

   
def load_sieker_wetland_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)

    user = request.user
    toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_wetland')
    user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))
    
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    wetlands = models.HistoricalWetlands.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    if wetlands.count() > 0:
        qs = models.ToolboxProject.objects.filter(
                Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
        
        feature_collection = create_feature_collection(wetlands)
        filter_form = HistoricalWetlandsFilter()
        slider_labels =  dict(models.WetlandFeasibility.objects.values_list('id', 'name_de').order_by('id'))

        html = render_to_string('toolbox/sieker_wetlands.html', {
            'project_select_form': project_select_form,
            'wetlands_filter': filter_form,
            
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_wetland').to_dict()

        return JsonResponse({'success': True, 'html': html, 'featureCollection': feature_collection,  'dataInfo': data_info, 'slider_labels': slider_labels})
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
    print('FROM filter_sieker_wetlands project', project)
    
    # filter landuses
    ids = project.get('selected_sieker_wetlands')
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
        data_info = models.DataInfo.objects.get(data_type='sieker_wetland').to_dict()
        data_info['featureColor'] = 'var(--bs-success)'
        data_info['dataType'] = 'filtered_sieker_wetland'

   

        data_info = models.DataInfo.objects.get(data_type='filtered_sieker_wetland').to_dict()
        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'featureCollection': feature_collection, 'message' : {'success': True}, 'dataInfo': data_info})


def load_injection_gui(request):
    user = request.user
    toolbox_type = models.ToolboxType.objects.get(name_tag='injection')
    
    qs = models.ToolboxProject.objects.filter(
            Q(user=user)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
    
    project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
    injection_weightings_form = forms.MarWeightingForm()
    suitability_aquifer_thickness = forms.SuitabilityForm('aquifer_thickness')
    suitability_depth_groundwater_form = forms.SuitabilityForm('depth_groundwater')
    suitability_land_use_form = forms.SuitabilityForm('land_use')
    suitability_distance_to_source_form = forms.SuitabilityForm('distance_to_source')
    suitability_distance_to_well_form = forms.SuitabilityForm('distance_to_well')
    suitability_hydraulic_conductivity = forms.SuitabilityForm('hydraulic_conductivity')

    slider_labels = dict(models.MarSliderDescription.objects.values_list('id', 'name_de').order_by('id'))
    slider_labels_suitability = dict(models.MarSuitabilitySliderDescription.objects.values_list('id', 'name_de').order_by('id'))


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

    }, request=request) 

    return JsonResponse({'success': True, 'html': html, 'slider_labels': slider_labels, 'slider_labels_suitability': slider_labels_suitability})

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
            print(f"✅ Cache for {workspace}:{layer_name} cleared successfully")
        elif r.status_code == 404:
            print(f"⚠️ Failed to clear cache: {r.status_code} - {r.text}")
            r.raise_for_status()
        else:
            print(f"⚠️ Failed to clear cache: {r.status_code} - {r.text}")
            r.raise_for_status()
    except:
        pass

def publish_raster_on_geoserver(layer_name, workspace='spreewassern_raster', style_name="style_raster_percent"):
    """
    Publishes a GeoTIFF to GeoServer as a coverage store and attaches an existing style.
    """

    delete_geoserver_layer(workspace, layer_name)

    
    url = f"{settings.GEOSERVER_URL}/rest/workspaces/{workspace}/coveragestores/{layer_name}/file.geotiff"
    with open(f"/app/raster_data/{layer_name}.tif", "rb") as f:
        r = requests.put(
            url,
            auth=HTTPBasicAuth(settings.GEOSERVER_USER, settings.GEOSERVER_PASS),
            headers={"Content-type": "image/tiff"},
            params={"configure": "all", "coverageName": layer_name},
            data=f
        )
    r.raise_for_status()
    print(f"Raster {layer_name} uploaded successfully")

    # Apply style
    layer_url = f"{settings.GEOSERVER_URL}/rest/layers/{workspace}:{layer_name}"
    style_xml = f"""
    <layer>
        <defaultStyle>
            <name>{style_name}</name>
        </defaultStyle>
    </layer>
    """
    r = requests.put(
        layer_url,
        auth=HTTPBasicAuth(settings.GEOSERVER_USER, settings.GEOSERVER_PASS),
        headers={"Content-type": "application/xml"},
        data=style_xml
    )
    r.raise_for_status()
    print(f"Style '{style_name}' applied to layer '{layer_name}'")


# requirements: rasterio, numpy, shapely (optional), pyproj
# pip install rasterio numpy shapely

def compute_suitability_from_tifs(suitability_dict, user):
    import os
    
        # We'll prepare a destination array for each raster, stacked into 3D array
    
        # out_masked, out_transform = mask(ref, [user_field.geom25833.geojson], crop=False, invert=False, indexes=1, nodata=np.nan, filled=False)

    with rasterio.open('raster_data/no_injection_area_mask.tif') as mask:
        nogo_mask = mask.read(1)
        dst_crs = mask.crs
        dst_transform = mask.transform
        dst_width = mask.width
        dst_height = mask.height
        dst_profile = mask.profile.copy()

    dst_profile['nodata'] = np.nan

    length_stack = len(suitability_dict) + 1
    stack = np.zeros((length_stack, dst_height, dst_width), dtype=np.float32)
    weighted_stack = np.zeros((2, dst_height, dst_width), dtype=np.float32)

    stack[0] = nogo_mask
    weighted_stack[0] = nogo_mask


    mask_arr = None  # to store mask for polygon later
    layer_weight_sum = 0
    for key in suitability_dict:
        layer_weight_sum += suitability_dict[key]['weight']
        
    i = 1
    for key in suitability_dict:
        
        path = suitability_dict[key]['map_path']
        
        # try:
        with rasterio.open(path) as src:
            dst_arr = src.read(1)
        
            dst_nodata = src.nodata
        new_arr = dst_arr.copy()
        new_arr = np.where(
            new_arr==dst_nodata,
            np.nan,
            new_arr
            )
        for k in suitability_dict[key]['mapping']:
            new_arr = np.where(
                new_arr==float(suitability_dict[key]['mapping'][k]['map_value']),
                suitability_dict[key]['mapping'][k]['score'],
                new_arr
                )
        stack[i] = new_arr
        weighted_stack[1] = weighted_stack[1] + (new_arr * suitability_dict[key]['weight'] / layer_weight_sum)
        
        i +=1
        # except:
        #     print(path)
    result_2d = np.prod(weighted_stack, axis=0) * 100

    with rasterio.open(f'raster_data/{user.id}_mar_result.tif', 'w', **dst_profile) as f:

        f.write(result_2d.astype(np.float32),1)

    i = 0
    for key in suitability_dict:
        i += 1
        print(i)
        with rasterio.open(f'raster_data/{user.id}_weighted_stack_{key}.tif', 'w', **dst_profile) as f:

            f.write(stack[i].astype(np.float32),1)
    
    publish_raster_on_geoserver(f"{user.id}_mar_result")


    return stack, weighted_stack, result_2d


        
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
        print('suitability dict:', suitability_dict)
        tif = compute_suitability_from_tifs(suitability_dict, user)


        return JsonResponse({'success': True})
    

################### BELOW IS NOT IN USE AND NOT WORKING ###############
# from django.http import HttpResponse, JsonResponse
ALLOWED_WMS_PARAMS = {
    "service",
    "request",
    "version",
    "layers",
    "layer",
    "styles",
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
    print("Received WMS request with params:", params)
    # Keep only allowed WMS params
    

    wms_params = {k: v for k, v in params.items() if k.lower() in ALLOWED_WMS_PARAMS}
    print("Forwarding params to GeoServer:", wms_params)

    response = requests.get(
        geoserver_url,
        params=wms_params,
    )

    return HttpResponse(
        response.content,
        content_type=response.headers.get("Content-Type")
    )


def load_sieker_drainage_gui(request, user_field_id):
    user = request.user
    if request.method == 'GET':
        toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_drainage')
        user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))
        qs = models.ToolboxProject.objects.filter(
            Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
        ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs)
        drainage_filter_form = forms.SiekerDrainageFilterForm()

        html = render_to_string('toolbox/sieker_drainage.html', {
            'project_select_form': project_select_form,
            'drainage_filter_form': drainage_filter_form,
        }, request=request)

        return JsonResponse({'success': True, 'html': html})
       