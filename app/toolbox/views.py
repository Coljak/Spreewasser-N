from django.shortcuts import render
from swn import models as swn_models
from swn import forms as swn_forms
from swn.views import load_nuts_polygon
from . import forms, models

from .filters import SiekerLargeLakeFilter,  SinkFilter, EnlargedSinkFilter, StreamFilter, LakeFilter, SiekerSinkFilter, GekRetentionFilter
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
from datetime import datetime

from shapely.geometry import shape as shapely_shape
from shapely.ops import nearest_points, transform
from pyproj import Transformer
from collections import defaultdict
import pandas as pd


transformer_25833_to_4326 = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)

def create_feature_collection(queryset):
    features = []
    for feature in queryset:
        
        features.append(feature.to_feature())
    return  {
        "type": "FeatureCollection",
        "features": features,
        }



# TOOLBOX GENERAL
def create_default_project(user):
    """
    Create a default project for the user.
    """
    default_project = models.ToolboxProject(
        name= '',
        user=user,
    ).to_json()

    return json.dumps(default_project, default=str)


def toolbox_dashboard(request):
    user = request.user
    projectregion = swn_models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    project_region = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }

    outline_injection = models.OutlineInjection.objects.first().geom.geojson
    outline_injection = json.loads(outline_injection)
    outline_injection = {
        "type": "Feature",
        "geometry": outline_injection,
        "properties": {
            "name": 'Spreewasser:N Injektionsbereich',
        }
    }

    outline_surface_water = models.OutlineSurfaceWater.objects.first().geom.geojson
    outline_surface_water = json.loads(outline_surface_water)
    outline_surface_water = {
        "type": "Feature",
        "geometry": outline_surface_water,
        "properties": {
            "name": 'Spreewasser:N Oberflächenwasser',
        }
    }

    outline_infiltration = models.OutlineInfiltration.objects.first().geom.geojson
    outline_infiltration = json.loads(outline_infiltration)
    outline_infiltration = {
        "type": "Feature",
        "geometry": outline_infiltration,
        "properties": {
            "name": 'Spreewasser:N Infiltrationsbereich',
        }
    }

    all_lakes = models.Lake25.objects.all()
    all_lakes_feature_collection = create_feature_collection(all_lakes)

    all_rivers = models.River.objects.all()
    all_rivers_feature_collection = create_feature_collection(all_rivers)
    
    print('all_rivers_feature_collection', all_rivers_feature_collection)

    
    state_county_district_form = swn_forms.PolygonSelectionForm(request.POST or None)
    project_select_form = forms.ToolboxProjectSelectionForm(user=user)
    # project_select_form = forms.ToolboxProjectSelectionForm()
    project_form = forms.ToolboxProjectForm()
    project_modal_title = 'Create new project'

    default_project = create_default_project(user)

    context = {
        'project_region': project_region,
        'default_project': default_project,
        'state_county_district_form': state_county_district_form,
        'project_select_form': project_select_form,
        'project_form': project_form,
        'project_modal_title': project_modal_title,
        'outline_injection': outline_injection,
        'outline_surface_water': outline_surface_water,
        'outline_infiltration': outline_infiltration,
        'all_lakes_feature_collection': all_lakes_feature_collection,
        'all_rivers_feature_collection': all_rivers_feature_collection,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)

def load_toolbox_project(request, id):

    project = models.ToolboxProject.objects.get(pk=id)
    print("Toolbox Project: ", project)
    if not project:
        return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    else:
        project_json = project.to_json()
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project_json})


def save_toolbox_project(request, project_id=None):
    print("CREATE Toolbox PROJECT\n", request.POST)
    if request.method == 'POST':
        user = request.user
        
        project_data = json.loads(request.body)
        toolbox_type = models.ToolboxType.objects.get(pk=project_data['toolboxType'])
        user_field = models.UserField.objects.get(pk=project_data['userField'])

        project = models.ToolboxProject.objects.create(
            name=project_data['name'],
            user=user,
            toolbox_type=toolbox_type,
            user_field=user_field,
            description=project_data['description']
        )
        project.save()

        return JsonResponse({
            'message': {
                'success': True, 
                'message': f'Project {project.name} saved'
                }, 
                'project_id': project.id, 
                'project_name': project.name
                })
    

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
            geom = json.loads(body['geom'])
            geos = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            user_field = None
            if body['id']:
                # Update existing UserField
                user_field = models.UserField.objects.get(id=body['id'])
                user_field.name = name
                user_field.geom_json = geom
                user_field.geom = geos
                
                user_field.save()
            else:
                user_field = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
                
                user_field.save()

            has_zalf_sinks = models.Sink.objects.filter(geom4326__within=user_field.geom).exists() or \
                             models.Sink.objects.filter(geom4326__intersects=user_field.geom).exists()
            has_zalf_enlarged_sinks = models.EnlargedSink.objects.filter(geom4326__within=user_field.geom).exists() or \
                                        models.EnlargedSink.objects.filter(geom4326__intersects=user_field.geom).exists()
            has_sieker_sink = models.SiekerSink.objects.filter(geom4326__within=user_field.geom).exists() or \
                              models.SiekerSink.objects.filter(geom4326__intersects=user_field.geom).exists()
            has_sieker_gek = models.GekRetention.objects.filter(geom4326__within=user_field.geom).exists() or \
                                models.GekRetention.objects.filter(geom4326__intersects=user_field.geom).exists()
            has_sieker_large_lake = models.SiekerLargeLake.objects.filter(geom4326__within=user_field.geom).exists() or \
                                        models.SiekerLargeLake.objects.filter(geom4326__intersects=user_field.geom).exists()
            user_field.has_zalf_sinks = has_zalf_sinks
            user_field.has_zalf_enlarged_sinks = has_zalf_enlarged_sinks
            user_field.has_sieker_sink = has_sieker_sink
            user_field.has_sieker_gek = has_sieker_gek
            user_field.has_sieker_large_lake = has_sieker_large_lake
            user_field.save()

            geo_json = json.loads(user_field.geom.geojson)
            geo_json['properties'] = {
                'name': user_field.name,
                'has_zalf_sinks': user_field.has_zalf_sinks,
                'has_zalf_enlarged_sinks': user_field.has_zalf_enlarged_sinks,
                'has_sieker_sink': user_field.has_sieker_sink,
                'has_sieker_gek': user_field.has_sieker_gek,
                'has_sieker_large_lake': user_field.has_sieker_large_lake,
            }   
            return JsonResponse({'name': user_field.name, 'geom_json': user_field.geom_json, 'id': user_field.id, 'new_user_field': geo_json})
        
    else:
        return HttpResponseRedirect('toolbox:toolbox_dashboard')

@login_required
def get_user_fields(request):
    if request.method == "GET":
        user_fields = models.UserField.objects.filter(user=request.user)
        user_projects = models.ToolboxProject.objects.filter(user=request.user)
        ufs = []
        for user_field in user_fields:
            uf = model_to_dict(user_field, fields=['id', 'user', 'name', 'geom_json'])
            uf['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
        # print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})

@login_required
def update_user_field(request, id):
    if request.method == 'POST':
        body = json.loads(request.body)
        name = body['name']
        geom = json.loads(body['geom'])
        geos = GEOSGeometry(body['geom'])
        # geos.transform(25833)
        user_field = models.UserField.objects.get(id=id)
        user_field.name = name
        user_field.geom_json = geom
        user_field.geom = geos
        user_field.save()
        
        return JsonResponse({'message': {'success': True, 'message': 'User field updated.'},'name': user_field.name, 'geom_json': user_field.geom_json, 'id': user_field.id})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'An error occurred updating the user field.'}})

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
    # user_projects = models.SwnProject.objects.filter(Q(user_field__id=id) & Q(user_field_user=request.user))
    user_projects = models.ToolboxProject.objects.filter(Q(user_field__id=id) & Q(user_field__user=request.user))
    print('user_projects:', user_projects)
    print('user_projects.values():', list(user_projects.values()))
    
    return JsonResponse({'projects': list(user_projects.values())})


#TODO needed?
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
    project_select_form = forms.ToolboxProjectSelectionForm()
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    sinks = models.Sink.objects.filter(
        centroid__within=user_field.geom
    )
    enlarged_sinks = models.EnlargedSink.objects.filter(
        centroid__within=user_field.geom
    )
    if sinks.count() > 0 or enlarged_sinks.count() > 0:
        streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        lakes = models.Lake.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        lake_form = LakeFilter(request.GET, queryset=lakes)
        stream_form = StreamFilter(request.GET, queryset=streams)
        sink_form = SinkFilter(request.GET, queryset=sinks)
        print("Queryset Sinks", sinks.count())
        enlarged_sink_form = EnlargedSinkFilter(request.GET, queryset=enlarged_sinks)

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
            geojson['properties']["index_sink_total_str"] = f'{index_sink_total}%'

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
        return JsonResponse({'feature_collection': feature_collection, 'dataInfo': data_info, 'message': message})
    

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
            geojson['properties']["index_sink_total_str"] = f'{index_sink_total}%'
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

        return JsonResponse({'feature_collection': feature_collection, 'dataInfo': data_info, 'message': message})

def filter_streams(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    distance = int(project.get('stream_distance_to_userfield', 0))
    streams = None
    if distance > 0:
        geom_25833 = user_field.geom.transform(25833, clone=True)
        
        geom_25833 = geom_25833.buffer(distance)
        buffered_4326 = geom_25833.transform(4326, clone=True)
        streams = models.Stream.objects.filter(Q(geom__intersects=buffered_4326) | Q(geom__within=buffered_4326))
    else:
        streams = models.Stream.objects.filter(Q(geom__intersects=geom) | Q(geom__within=geom))

    filters = Q()
    filters = add_range_filter(filters, project, 'stream_min_surplus_volume', 'min_surplus_volume')
    filters = add_range_filter(filters, project, 'stream_mean_surplus_volume', 'mean_surplus_volume')
    filters = add_range_filter(filters, project, 'stream_max_surplus_volume', 'max_surplus_volume')
    filters = add_range_filter(filters, project, 'stream_plus_days', 'plus_days')
    streams = streams.filter(filters)

    
    features = []
    print("COUNT(Streams)", streams.count())
    if streams.count() == 0:
        message = {
            'success': False, 
            'message': f'No streams found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No streams found.'}})
    else:
        
        for stream in streams:
            geom = stream.geom
            geojson = json.loads(geom.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": stream.id,
                "name": stream.name,
                "minimum_environmental_flow": stream.minimum_environmental_flow,
                "fgw_id": stream.fgw_id,
                # "centroid": geom.centroid,
                "shape_length": round(stream.shape_length, 2),
                "min_surplus_volume": round(stream.min_surplus_volume, 2),
                "mean_surplus_volume": round(stream.mean_surplus_volume, 2),
                "max_surplus_volume": round(stream.max_surplus_volume, 2),
                "plus_days": stream.plus_days,
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }

        message = {
            'success': True, 
            'message': f'Found {streams.count()} streams'
        }

        print('feature_collection:', feature_collection)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def filter_lakes(request):
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
        lakes = models.Lake.objects.filter(Q(geom__intersects=buffer_4326) | Q(geom__within=buffer_4326))
    else:
        lakes = models.Lake.objects.filter(Q(geom__intersects=geom) | Q(geom__within=geom))

    filter = Q()
    filter = add_range_filter(filter, project, 'lake_min_surplus', 'min_surplus_volume')
    filter = add_range_filter(filter, project, 'lake_mean_surplus', 'mean_surplus_volume')
    filter = add_range_filter(filter, project, 'lake_max_surplus', 'max_surplus_volume')
    filter = add_range_filter(filter, project, 'lake_plus_days', 'plus_days')
    lakes = lakes.filter(filter)

    if lakes.count() == 0:
        message = {
            'success': False, 
            'message': f'No lakes found in the search area.'
        }
        return JsonResponse({'message': {'success': False, 'message': 'No lakes found.'}})
    else:
        features = []
        for lake in lakes:
            # geom = lake.centroid
            geom = lake.geom
            # geom = GEOSGeometry(lake.geom)
            geojson = json.loads(geom.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": lake.id,
                "name": lake.name,
                "min_surplus_volume": int(lake.min_surplus_volume),
                "mean_surplus_volume": int(lake.mean_surplus_volume),
                "max_surplus_volume": int(lake.max_surplus_volume),
                "plus_days": lake.plus_days,
                "shape_length": int(lake.shape_length),
                "shape_area": int(lake.shape_area),
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {lakes.count()} lakes'
        }
        print('feature_collection:', feature_collection)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})
        

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
            # 'forest_weighting': ForestWeightingFilter(),
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
            if is_enlarged_sink:
                if sink.sink_embankment.first():
                    sink_embankment = sink.sink_embankment.first()
                    result['sink_embankment'] = sink_embankment.to_feature()
                

            results.append(result)
            

    return results


def get_inlets(request):
    # POST request
    project = json.loads(request.body)
    print('Project:', project)

    sinks = models.Sink.objects.filter(id__in=project.get('selected_sinks', []))
    enlarged_sinks = models.EnlargedSink.objects.filter(id__in=project.get('selected_enlarged_sinks', []))
    lakes = models.Lake.objects.filter(id__in=project.get('selected_lakes', []))
    streams = models.Stream.objects.filter(id__in=project.get('selected_streams', []))

    inlets_sinks = get_shortest_connection_lines_utm(sinks, lakes, streams)
    inlets_enlarged_sinks = get_shortest_connection_lines_utm(enlarged_sinks, lakes, streams)
    
    # inlets_sinks = get_result_features(sinks, lakes, streams)
    # inlets_enlarged_sinks = get_result_features(enlarged_sinks, lakes, streams)
    
    response = {
        'inlets_sinks': inlets_sinks + inlets_enlarged_sinks,
        'message': {
            'success': True,
            'message': f'Found {len(inlets_sinks)} pipes for sinks and {len(inlets_enlarged_sinks)} pipes for enlarged sinks.'
        }
    }
    print(response)
    return JsonResponse(response)

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
        project_select_form = forms.ToolboxProjectSelectionForm()
        sieker_lake_filter = SiekerLargeLakeFilter(request.GET, queryset=lakes)

        water_levels = models.SiekerWaterLevel.objects.filter(
            geom4326__within=user_field.geom
        )
        lakes_feature_collection = create_feature_collection(lakes)
        water_levels_feature_collection = create_feature_collection(water_levels)

        lakes_data_info = models.DataInfo.objects.get(data_type='sieker_large_lake').to_dict()
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
            # 'sink_form': sink_form, 
            # 'enlarged_sink_form': enlarged_sink_form,
            'project_select_form': project_select_form,
            'sieker_lake_filter': sieker_lake_filter,      
        }, request=request) 

        return JsonResponse({'success': True, 'layers': layers , 'html': html, 'data_info': lakes_data_info})
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
        features = []
        for lake in lakes:
            features.append(lake.to_feature())
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
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
    project_select_form = forms.ToolboxProjectSelectionForm()
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    sinks = models.SiekerSink.objects.filter(
        centroid__within=user_field.geom
    )

    if sinks.count() > 0:
        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        sieker_sink_filter = SiekerSinkFilter(request.GET, queryset=sinks)

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
    print("Sinks:", sinks.count())
    filters = Q()
    filters = add_range_filter(filters, project, 'area', 'area')
    filters = add_range_filter(filters, project, 'volume', 'volume')
    filters = add_range_filter(filters, project, 'sink_depth', 'sink_depth')
    filters = add_range_filter(filters, project, 'avg_depth', 'avg_depth')
    filters = add_range_filter(filters, project, 'urbanarea_percent', 'urbanarea_percent')
    filters = add_range_filter(filters, project, 'avg_depth', 'avg_depth')
    
    sinks = sinks.filter(filters)
    print("Sinks FILTERED:", sinks.count())

    feasibility = project.get('feasibility', [])
    feasibility = (Q(umsetzbark__in=feasibility))
    sinks = sinks.filter(feasibility)
    print("Sieker Sinks LAND USE FILTERED:", sinks.count())
    if sinks.count() == 0:
        message = {
            'success': False, 
            'message': f'No sinks found in the search area.'
        }
        return JsonResponse({'message': message})
    else:
        print("Sinks", sinks.count())
        
        

        features = []
        for sink in sinks:
            centroid = sink.centroid
            geojson = json.loads(centroid.geojson)

            print('geojson:', geojson)
            geojson['properties'] = {
                "id": sink.id,
                "sink_depth": round(sink.sink_depth, 2),
                "area": round(sink.area, 1),
                "volume": round(sink.volume, 1),
                "avg_depth": round(sink.avg_depth, 1),
                "max_elevation": round(sink.max_elevation, 1),
                "min_elevation": round(sink.min_elevation, 1),
                "urbanarea_percent": sink.urbanarea_percent,
                "wetlands_percent": sink.wetlands_percent,
                "distance_t": sink.distance_t,
                "dist_lake": sink.dist_lake,
                "waterdist": sink.waterdist,
                "umsetzbark": sink.umsetzbark,
               
            }
            features.append(geojson)
        feature_collection = {
            "type": "FeatureCollection",
            "features": features,
            }
        message = {
            'success': True, 
            'message': f'Found {sinks.count()} sinks'
        }
        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'feature_collection': feature_collection, 'message': message})
    
   
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
        project_select_form = forms.ToolboxProjectSelectionForm()
        
        feature_collection = create_feature_collection(geks)

        gek_filter_form = GekRetentionFilter(request.GET, queryset=geks)
        slider_labels = dict(models.GekPriority.objects.values_list("priority_level", "description_de").distinct().order_by("priority_level"))

        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        # sieker_geks_filter = SiekerGekFilter(request.GET, queryset=geks)

        html = render_to_string('toolbox/sieker_gek.html', {
            'project_select_form': project_select_form,
            'gek_filter_form': gek_filter_form  ,
            
            # 'sieker_sink_filter': sieker_geks_filter,
            
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_gek').to_dict()

        return JsonResponse({'success': True, 'html': html, 'gek_retention': feature_collection, 'slider_labels': slider_labels, 'data_info': data_info})
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
    
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    wetlands = models.HistoricalWetlands.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    # all_sieker_wetland_ids = [g.id for g in wetlands]
   

    if wetlands.count() > 0:
        project_select_form = forms.ToolboxProjectSelectionForm()
        
        feature_collection = create_feature_collection(wetlands)

        # wetland_filter_form = GekRetentionFilter(request.GET, queryset=wetlands)
        # slider_labels = dict(models.GekPriority.objects.values_list("priority_level", "description_de").distinct().order_by("priority_level"))

        # streams = models.Stream.objects.filter(Q(geom__intersects=user_field.geom) | Q(geom__within=user_field.geom))

        # sieker_wetlands_filter = SiekerGekFilter(request.GET, queryset=wetlands)

        html = render_to_string('toolbox/sieker_wetlands.html', {
            'project_select_form': project_select_form,
            # 'wetland_filter_form': wetland_filter_form  ,
            
            # 'sieker_sink_filter': sieker_wetlands_filter,
            
        }, request=request) 
        data_info = models.DataInfo.objects.get(data_type='sieker_wetland').to_dict()

        return JsonResponse({'success': True, 'html': html, 'wetlands': feature_collection,  'data_info': data_info})
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
    
    # wetlands = models.GekRetention.objects.filter(Q(geom4326__intersects=user_field.geom) | Q(geom4326__within=user_field.geom))
    # filter landuses
    ids = project.get('selected_sieker_wetlands')
    wetlands = models.GekRetention.objects.filter(pk__in=ids)
    landuses = models.GekLanduse.objects.filter(Q(wetland_retention__in=wetlands) & Q(clc_landuse__id__in=project['wetland_landuse']))
    wetlands = models.GekRetention.objects.filter(landuses__in=landuses).distinct()
    print("Geks:", wetlands.count())

    # filter measures
    filters = Q(priority__priority_level__gte=project['wetland_priority'])
    filters = add_range_filter(filters, project, 'wetland_costs', 'costs') 

    measures = models.GekRetentionMeasure.objects.filter(
            wetland_retention__in=wetlands
        ).filter(filters)
    
    wetlands = models.GekRetention.objects.filter(measures__in=measures).distinct()


    print("Geks FILTERED:", wetlands.count())


    if wetlands.count() == 0:
        message = {
            'success': False, 
            'message': f'Es sind keine Gewässerentwicklungskonzepte für diese Filtereinstellungen bekannt.'
        }
        return JsonResponse({'message': message})
    else:
        print("Geks", wetlands.count())
        
        feature_collection = create_wetland_feature_collection(wetlands)
        data_info = models.DataInfo.objects.get(data_type='sieker_wetland').to_dict()
        data_info['featureColor'] = 'var(--bs-success)'

        dict_list = []
        for wetland in wetlands:
            d = wetland.to_dict()
            d['measures'] = [m.to_dict() for m in measures if m.wetland_retention == wetland]
            dict_list.append(d)
            
        print('measures: ', dict_list)

        data_info = models.DataInfo.objects.get(data_type='filtered_sieker_wetland').to_dict()
        print('Time for filter_sinks:', datetime.now() - start)
        return JsonResponse({'featureCollection': feature_collection, 'message' : {'success': True}, 'dataInfo': data_info, 'measures': dict_list})
