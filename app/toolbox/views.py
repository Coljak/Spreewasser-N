from django.shortcuts import render
from swn import models as swn_models
from swn import forms as swn_forms
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
FLOAT32_NODATA = np.float32(-3.4028235e+38)

def boolean_translation(bool, language='de'):
    translation = {
        True: {'de': 'Ja', 'en': 'Yes'},
        False: {'de': 'Nein', 'en': 'No'}
    }
    return translation[bool][language]

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



def toolbox_dashboard(request):
    user = request.user
    project_region = swn_models.ProjectRegion.objects.first().to_feature()

    outline_injection = models.OutlineInjection.objects.first().to_feature()

    outline_surface_water = models.OutlineSurfaceWater.objects.first().to_feature()

    outline_infiltration = models.OutlineInfiltration.objects.first().to_feature()


    state_county_district_form = swn_forms.PolygonSelectionForm(request.POST or None)

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
        ufs = []
        for user_field in user_fields:
            uf = user_field.to_feature()
            uf['properties']['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
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
            }
        message = {
            'success': True, 
            'message': f'Es wurden {sinks.count()} Senken gefunden.'
        }

        data_info = models.DataInfo.objects.get(data_type=sink_type).to_dict()

        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    

def filter_waterbodies(request):

    try:
        request = json.loads(request.body)
        project = request['project']
        data_type = request['dataType']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if data_type in ('lake', 'sieker_lake'):
        waterbody_class = models.Lake
        waterbody = 'Seen'
    elif data_type in ('stream', 'sieker_stream'):
        waterbody = 'Flüsse'
        waterbody_class = models.Stream

    data_info = models.DataInfo.objects.get(data_type=data_type).to_dict()

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



def new_shortest_connection(sink, lakes, streams, transform_to_4326=True, connection_id=0):
    """
    This function works for sinks, enlarged sinks and sieker sinks.
    It returns a dictionary with the sink.id as key and a linefeature with properties as values.
    """
    print('new_shortest_connection')

    print('new_shortest_connection 1')
    lake_with_distance = lakes.annotate(
        distance_to_sink=Distance('geom25833', sink.geom25833)
        ).order_by('distance_to_sink').first()
    
    stream_with_distance = streams.annotate(
        distance_to_sink=Distance('geom25833', sink.geom25833)
        ).order_by('distance_to_sink').first()
    
    closest = lake_with_distance if lake_with_distance is not None else stream_with_distance
    print('new_shortest_connection 2')
    if (
        (lake_with_distance and stream_with_distance) and
        (lake_with_distance.distance_to_sink.m > stream_with_distance.distance_to_sink.m)
        ):
        print('new_shortest_connection 2a')
        closest = stream_with_distance
    print('new_shortest_connection 3 closest', closest)

    distance_m=int(closest.distance_to_sink.m)
    

    # create a line feature
    pt1, pt2 = nearest_points(
        shapely_shape(json.loads(sink.geom25833.geojson)),
        shapely_shape(json.loads(closest.geom25833.geojson))
    )
    line = LineString([pt1.coords[0], pt2.coords[0]])
    line_geom = GEOSGeometry(line.wkt, srid=25833)

    print('new_shortest_connection 5')
    if transform_to_4326:
        line_geom.transform(4326)
    print('new_shortest_connection 6')
    connection_data = {
        'id': connection_id,
        'sink_id': sink.id,  
        'sink_type': sink.__data_type__(),
        'closest_waterbody_type': closest.__data_type__(),
        'closest_waterbody_id': closest.id,
        'closest_fgw_id': closest.fgw_id,
        'closest_waterbody': closest.to_json(),   
        'waterbody_name': closest.name,       
        'distance_m': distance_m,
        'connection_feature': {
            "type": "Feature",
            "geometry": json.loads(line_geom.geojson),
            "properties": {
                'id': connection_id,
                'sink_id': sink.id,
                'closest_waterbody_type': closest.__data_type__(),
                'closest_waterbody_id': closest.id,
                'distance_m': distance_m,
            },
        },
    }

    
    
    print('new_shortest_connection 7')
    return connection_data
            
def get_infiltration_result_list(project, epsg=4326):
    '''
    this gets the results from an infiltration project. 
    The function is used for display and data download.
    '''

    language='de'
    sinks = models.Sink.objects.filter(id__in=project.get('selected_sinks', []))
    enlarged_sinks = models.EnlargedSink.objects.filter(id__in=project.get('selected_enlarged_sinks', []))
    lakes = models.Lake.objects.filter(id__in=project.get('selected_lakes', []))
    streams = models.Stream.objects.filter(id__in=project.get('selected_streams', []))


    def rate_water_sink_distance(distance):
        if distance >= 2000:
            rating_length = 0
        elif distance >= 1000:
            rating_length = 5
        else:
            rating_length = int((1000 - distance)/10)
        return rating_length
    
    
    def rate_connection(connection_data, sink, indices):

        index_length = \
                rate_water_sink_distance(connection_data['distance_m'])
        index_volumes = \
            min(connection_data['closest_waterbody']['mean_surplus_volume'] / sink.volume, 1) *100
        print('index_volume', index_volumes)
        index_connection = (index_length + index_volumes)/ 2
        print('index_connection', index_connection)
        connection_data['connection_feature']['properties']['index_length'] = round(index_length)
        connection_data['connection_feature']['properties']['index_volumes'] = round(index_volumes)
        connection_data['connection_feature']['properties']['index_inlet'] = round(index_connection)
        connection_data['index_inlet'] = round(index_connection)
        index_sink = min(int(indices[sink.id]['index_sink_total'] *100), 100)
        connection_data['index_sink'] = index_sink
        index_total = int((index_connection + index_sink) / 2)
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
            }
        for i, sink in enumerate(sinks):
            connection_data = new_shortest_connection(sink, lakes, streams, i)
            
            
            connection_data['is_enlarged_sink'] = boolean_translation(False, language)
            # connection_data['sink_feature'] = sink.to_feature(indices_sinks, epsg=epsg)

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
            }
        for i, sink in enumerate(enlarged_sinks):
            connection_data = new_shortest_connection(sink, lakes, streams, sink_count + i)
            connection_data['is_enlarged_sink'] = boolean_translation(True, language)
            connection_data = rate_connection(connection_data, sink, indices_enlarged_sinks)
            line_feature = connection_data['connection_feature']
            connection_data.pop('connection_feature')
            
            # connection_data['sink_feature'] = sink.to_feature(indices_enlarged_sinks, epsg=epsg)
            
            results.append(connection_data)
            line_features.append(line_feature)
        
    result_dict['inlet_feature_collection'] = {
        "type": "FeatureCollection",
        "features": line_features,
    }
    result_dict['results'] = results
    print(results)

    
    return result_dict

### NEW 2025-11-15
def get_infiltration_results(request):
    # POST request
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    # try:
    project = request.body
    print('Project:', type(project))
    project = json.loads(project)


    results_dict = get_infiltration_result_list(project, epsg=4326)
    result_data_info = models.DataInfo.objects.get(data_type='infiltration_result')
    inlet_data_info = models.DataInfo.objects.get(data_type='infiltration_inlet')
    sink_data_info = models.DataInfo.objects.get(data_type='infiltration_result_sink')
    enlarged_sink_data_info = models.DataInfo.objects.get(data_type='infiltration_result_enlarged_sink')
    
    
    response = {
        'inlet_data_info': inlet_data_info.to_dict(),
        'sink_data_info': sink_data_info.to_dict(),
        'enlarged_sink_data_info': enlarged_sink_data_info.to_dict(), 
        'result_data_info': result_data_info.to_dict(),

        'results': results_dict['results'],

        'inlet_feature_collection': results_dict.get('inlet_feature_collection', None),
        'sink_feature_collection' : results_dict.get('sink_feature_collection', None),
        'enlarged_sink_feature_collection': results_dict.get('enlarged_sink_feature_collection', None),
        
        'message': {
            'success': True,
        }
    }
    print('response', response)
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
def sieker_surface_waters_gui(request, user_field_id):
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

        water_levels = models.SiekerWaterLevel.objects.filter(
            geom4326__within=user_field.geom
        )
        water_levels_feature_collection = create_feature_collection(water_levels)
        water_levels_data_info = models.DataInfo.objects.get(data_type='sieker_water_level').to_dict()

        result_form = forms.SiekerSurfaceWaterResultDownloadForm()


        water_levels = {
                'featureCollection': water_levels_feature_collection,
                'dataInfo': water_levels_data_info
                }


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

        return JsonResponse({'success': True, 'water_levels': water_levels , 'html': html, 'default_project': default_project})
    else:
        return JsonResponse({'success': False, 'message': 'Im Suchgebiet befinden sich keine geeigneten Seen.'})

    
## Sieker Oberflächengewässer / Large Lakes / Surface Waters
def filter_sieker_surface_waters(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])

    # distance = int(project.get('lake_distance_to_userfield', 0))
    # lakes = None
    # if distance > 0:
        # Transform to EPSG:25833 (meters) and add the buffer
    #     user_geom_25833 = user_field.geom.transform(25833, clone=True)
    #     buffer_25833 = user_geom_25833.buffer(distance)
    #     buffer_4326 = buffer_25833.transform(4326, clone=True)
    #     lakes = models.SiekerLargeLake.objects.filter(Q(geom__intersects=buffer_4326) | Q(geom__within=buffer_4326))
    # else:
    lakes_data_info = models.DataInfo.objects.get(data_type='sieker_surface_water').to_dict()
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

    lakes_data_info = models.DataInfo.objects.get(data_type='sieker_surface_water').to_dict()
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
            'message': 'Im Suchgebiet entsprechen keine Senken den Filterkriterien.'
        }
        return JsonResponse({'message': message})
    else:
        
        data_info = models.DataInfo.objects.get(data_type='sieker_sink').to_dict()
        feature_collection = create_point_feature_collection(sinks)
        message = {
            'success': True, 
            'message': f'Es wurden {sinks.count()} Senken gefunden.'
        }
        return JsonResponse({'featureCollection': feature_collection, 'dataInfo': data_info, 'message': message})
    
   
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

        html = render_to_string('toolbox/sieker_gek.html', {
            'project_select_form': project_select_form,
            'gek_filter_form': gek_filter_form ,
            'result_form': result_form,
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_dict()

        return JsonResponse({'success': True, 'html': html, 'featureCollection': feature_collection, 'slider_labels': slider_labels, 'dataInfo': data_info, 'default_project': default_project})
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
         return JsonResponse({'message':{'success': False, 'message': 'Es ist kein Suchgebiet ausgewählt oder es existiert nicht..'}})
    else:
        user_field_id = int(user_field_id)

    user = request.user
    toolbox_type = models.ToolboxType.objects.get(name_tag='sieker_wetland')
    user_field = models.UserField.objects.get(Q(id=int(user_field_id))&Q(user=user))
    
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    
    wetlands = models.HistoricalWetlands.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))

    if wetlands.count() > 0:
        qs = models.ToolboxProject.objects.filter(
                Q(user_field=user_field)&Q(toolbox_type=toolbox_type)
            ).order_by('-creation_date').reverse()
        project_select_form = forms.ToolboxProjectSelectionForm(qs=qs, data_type='sieker_wetland')
        
        feature_collection = create_feature_collection(wetlands)
        filter_form = filters.HistoricalWetlandsFilter()
        slider_labels =  dict(models.WetlandFeasibility.objects.values_list('id', 'name_de').order_by('id'))
        # TODO This does not really make sense - more filters?
        result_form = forms.SiekerWetlandDownloadForm()
        default_project = filters.create_default_project(
            user_field,
            [
                filter_form,
                result_form,
                ],
            'sieker_wetland'
        )
        html = render_to_string('toolbox/sieker_wetlands.html', {
            'project_select_form': project_select_form,
            'wetlands_filter': filter_form,
            'result_form': result_form,
            
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_wetland').to_dict()

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

# def compute_suitability_from_tifs(suitability_dict, user):

#     with rasterio.open('raster_data/no_injection_area_mask.tif') as mask:
#         nogo_mask = mask.read(1)
#         dst_crs = mask.crs
#         dst_transform = mask.transform
#         dst_width = mask.width
#         dst_height = mask.height
#         dst_profile = mask.profile.copy()

#     dst_profile['nodata'] = FLOAT32_NODATA

#     length_stack = len(suitability_dict) + 1
#     stack = np.zeros((length_stack, dst_height, dst_width), dtype=np.float32)
#     weighted_stack = np.zeros((2, dst_height, dst_width), dtype=np.float32)

#     stack[0] = nogo_mask
#     weighted_stack[0] = nogo_mask


#     mask_arr = None  # to store mask for polygon later
#     layer_weight_sum = 0
#     for key in suitability_dict:
#         layer_weight_sum += suitability_dict[key]['weight']
        
#     i = 1
#     for key in suitability_dict:
        
#         path = suitability_dict[key]['map_path']
        
#         # try:
#         with rasterio.open(path) as src:
#             dst_arr = src.read(1)
        
#             dst_nodata = src.nodata
#         new_arr = dst_arr.copy()
#         new_arr = np.where(
#             new_arr==dst_nodata,
#             FLOAT32_NODATA,
#             new_arr
#             )
#         for k in suitability_dict[key]['mapping']:
#             new_arr = np.where(
#                 new_arr==float(suitability_dict[key]['mapping'][k]['map_value']),
#                 suitability_dict[key]['mapping'][k]['score'],
#                 new_arr
#                 )
#         stack[i] = new_arr
#         weighted_stack[1] = weighted_stack[1] + (new_arr * suitability_dict[key]['weight'] / layer_weight_sum)
        
#         i +=1
#         # except:
#         #     print(path)
#     result_2d = np.prod(weighted_stack, axis=0) * 100

#     with rasterio.open(f'raster_data/{user.id}_mar_result.tif', 'w', **dst_profile) as f:

#         f.write(result_2d.astype(np.float32),1)

#     i = 0
#     for key in suitability_dict:
#         i += 1
#         print(i)
#         with rasterio.open(f'raster_data/{user.id}_weighted_stack_{key}.tif', 'w', **dst_profile) as f:

#             f.write(stack[i].astype(np.float32),1)
    
#     publish_raster_on_geoserver(f"{user.id}_mar_result")


#     return stack, weighted_stack, result_2d


        

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
        # except:
        #     print(path)
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
        drained_areas = models.DrainedArea.objects.all()
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
        print('drainage_types', drained_area_types)
        drainage_type_feature_collections = []
        for dt in drained_area_types:          
            drainage_type_feature_collections.append({
                'drainedAreaTypeId': dt.id,
                'dataInfo': models.DataInfo.objects.get(data_type=dt.name_tag).to_dict(),
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
                'dataInfo': models.DataInfo.objects.get(data_type=detail.name_tag).to_dict(),
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
       