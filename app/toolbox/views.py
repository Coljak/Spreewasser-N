from django.shortcuts import render
from . import models
from swn import models as swn_models
from swn import forms as swn_forms
from . import forms
from .filters import SinkFilter, EnlargedSinkFilter, LakeFilter, StreamFilter


from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.forms.models import model_to_dict
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.db.models import Max, Min
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db.models import F, Q

from django.contrib.gis.db.models import PointField
from django.db import connection
# Create your views here.


# def test(request):
#     context = {
#         'form': forms.ToolboxProjectForm()
#     }
#     return render(request, 'toolbox/test.html', context)





def test(request):
    sink_filter = SinkFilter(request.GET)
    enlarged_sink_filter = EnlargedSinkFilter(request.GET)

    # single_widget = forms.SingleWidgetForm()
    # double_widget = forms.DoubleWidgetForm()
    double_widget = forms.CustomRangeSliderWidget()
    single_widget = forms.CustomSingleSliderWidget()
    return render(request, 'toolbox/test.html', {'sink_filter':sink_filter, 'enlarged_sink_filter': enlarged_sink_filter, 'single_widget': single_widget, 'double_widget': double_widget})

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

    outline_geste = models.OutlineGeste.objects.first().geom.geojson
    outline_geste = json.loads(outline_geste)
    outline_geste = {
        "type": "Feature",
        "geometry": outline_geste,
        "properties": {
            "name": 'Spreewasser:N Geste',
        }
    }
    
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
        'outline_geste': outline_geste,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)




def load_infiltration_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)
    project_select_form = forms.ToolboxProjectSelectionForm()
    user_field = models.UserField.objects.get(Q(id=user_field_id)&Q(user=request.user))
    if user_field is None:
        return JsonResponse({'message':{'success': False, 'message': 'User field not found or selected.'}})
    
    user_field_geom = GEOSGeometry(user_field.geom)
    sinks = models.Sink4326.objects.filter(
        centroid__within=user_field.geom
    )
    enlarged_sinks = models.EnlargedSink4326.objects.filter(
        centroid__within=user_field.geom
    )
    streams = models.Stream4326.objects.filter(
        geom__within=user_field.geom
    )
    lakes = models.Lake4326.objects.filter(
        geom__within=user_field.geom
    )

    

    lake_form = LakeFilter(request.GET, queryset=lakes)
    stream_form = StreamFilter(request.GET, queryset=streams)
    sink_form = SinkFilter(request.GET, queryset=sinks)
    print("Queryset Sinks", sinks.count())
    enlarged_sink_form = EnlargedSinkFilter(request.GET, queryset=enlarged_sinks)

    html = render_to_string('toolbox/infiltration.html', {
        # 'sink_form': sink_form, 
        # 'enlarged_sink_form': enlarged_sink_form,
        'project_select_form': project_select_form,
        'sink_filter': sink_form,
        'enlarged_sink_filter': enlarged_sink_form,
        'streams_form': stream_form,
        'lakes_form': lake_form,
    }, request=request) 

    return JsonResponse({'html': html})




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




def filter_sinks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    sinks = models.Sink4326.objects.filter(geom__within=geom)
    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'sink_area', 'area')
    filters = add_range_filter(filters, project['infiltration'], 'sink_volume', 'volume')
    filters = add_range_filter(filters, project['infiltration'], 'sink_depth', 'depth')
    filters = add_range_filter(filters, project['infiltration'], 'sink_index_soil', 'index_soil')
    print("Sinks", sinks.count())
    sinks = sinks.filter(filters)
    print("Sinks", sinks.count())

    
    land_use_values = project['infiltration'].get('sink_land_use', [])
    land_use_filter = (
        Q(land_use_1__in=land_use_values) &
        (Q(land_use_2__in=land_use_values) |
        Q(land_use_2__isnull=True)) &
        (Q(land_use_3__in=land_use_values) |
        Q(land_use_3__isnull=True))
        )
    sinks = sinks.filter(land_use_filter)
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
                "depth": sink.depth,
                "area": sink.area,
                "volume": sink.volume,
                "index_soil": str(sink.index_soil * 100) + "%",
                "land_use_1": sink.land_use_1,
                "land_use_2": sink.land_use_2,
                "land_use_3": sink.land_use_3,
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
        return JsonResponse({'feature_collection': feature_collection, 'message': message})



def filter_enlarged_sinks(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    sinks = models.EnlargedSink4326.objects.filter(geom__within=geom)

    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_area', 'area')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume', 'volume')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_depth', 'depth')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume_construction_barrier', 'volume_construction_barrier')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_volume_gained', 'volume_gained')
    filters = add_range_filter(filters, project['infiltration'], 'enlarged_sink_index_soil', 'index_soil')
    sinks = sinks.filter(filters)


    land_use_values = project['infiltration'].get('enlarged_sink_land_use', [])
    land_use_filter = (
        Q(land_use_1__in=land_use_values) &
        (Q(land_use_2__in=land_use_values) |
        Q(land_use_2__isnull=True)) &
        (Q(land_use_3__in=land_use_values) |
        Q(land_use_3__isnull=True)) &
        (Q(land_use_4__in=land_use_values) |
        Q(land_use_4__isnull=True))
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
        for sink in sinks:
            centroid = sink.centroid
            geojson = json.loads(centroid.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": sink.id,
                "depth": sink.depth,
                "area": sink.area,
                "volume": sink.volume,
                "volume_construction_barrier": sink.volume_construction_barrier,
                "volume_gained": sink.volume_gained,
                "index_soil": str(sink.index_soil * 100) + "%",
                "land_use_1": sink.land_use_1,
                "land_use_2": sink.land_use_2,
                "land_use_3": sink.land_use_3,
                "land_use_4": sink.land_use_4,
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

        return JsonResponse({'feature_collection': feature_collection, 'message': message})


def filter_streams(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    streams = models.Stream4326.objects.filter(geom__within=geom)

    filters = Q()
    filters = add_range_filter(filters, project['infiltration'], 'stream_min_surplus', 'min_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_mean_surplus', 'mean_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_max_surplus', 'max_surplus_volume')
    filters = add_range_filter(filters, project['infiltration'], 'stream_plus_days', 'plus_days')
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
                "min_surplus_volume": stream.min_surplus_volume,
                "mean_surplus_volume": stream.mean_surplus_volume,
                "max_surplus_volume": stream.max_surplus_volume,
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

        return JsonResponse({'feature_collection': feature_collection, 'message': message})

def filter_lakes(request):
    try:
        project = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_field = models.UserField.objects.get(pk=project['userField'])
    geom = GEOSGeometry(user_field.geom)
    lakes = models.Lake4326.objects.filter(geom__within=geom)
    filter = Q()
    filter = add_range_filter(filter, project['infiltration'], 'lake_min_surplus', 'min_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_mean_surplus', 'mean_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_max_surplus', 'max_surplus_volume')
    filter = add_range_filter(filter, project['infiltration'], 'lake_plus_days', 'plus_days')
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
            geom = lake.geom
            geojson = json.loads(geom.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": lake.id,
                "min_surplus_volume": lake.demin_surplus_volumepth,
                "mean_surplus_volume": lake.mean_surplus_volume,
                "max_surplus_volume": lake.max_surplus_volume,
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

        return JsonResponse({'feature_collection': feature_collection, 'message': message})



# def get_selected_sinks(request):
#     if request.method == 'POST':
#         try:
#             project = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)

#         user_field = models.UserField.objects.get(pk=project['userField'])
#         geom = GEOSGeometry(user_field.geom)
#         sinks = []
#         if project.get('enlargedSink') is True:
#             sinks = models.EnlargedSink4326.objects.filter(geom__within=geom)
#             sinks = sinks.filter(
#                 depth__gte=float(project['infiltration']['enlargedSinkDepthMin']),
#                 depth__lte=float(project['infiltration']['enlargedSinkDepthMax']),
#                 area__gte=float(project['infiltration']['enlargedSinkAreaMin']),
#                 area__lte=float(project['infiltration']['enlargedSinkAreaMax']),
#                 volume__gte=float(project['infiltration']['enlargedSinkVolumeMin']),
#                 volume__lte=float(project['infiltration']['enlargedSinkVolumeMax']),
#             )
            
#         else:
#             sinks = models.Sink4326.objects.filter(geom__within=geom)
#             sinks = sinks.filter(
#                 depth__gte=float(project['infiltration']['sinkDepthMin']),
#                 depth__lte=float(project['infiltration']['sinkDepthMax']),
#                 area__gte=float(project['infiltration']['sinkAreaMin']),
#                 area__lte=float(project['infiltration']['sinkAreaMax']),
#                 volume__gte=float(project['infiltration']['sinkVolumeMin']),
#                 volume__lte=float(project['infiltration']['sinkVolumeMax']),
#             )

#         features = []
#         for sink in sinks:
#             centroid = sink.centroid
#             geojson = json.loads(centroid.geojson)
#             print('geojson:', geojson)
#             geojson['properties'] = {
#                 "id": sink.id,
#                 "depth": sink.depth,
#                 "area": sink.area,
#                 "index_soil": str(sink.index_soil * 100) + "%",
#                 "land_use_1": sink.land_use_1,
#                 "land_use_2": sink.land_use_2,
#                 "land_use_3": sink.land_use_3,
#             }
#             features.append(geojson)
#         feature_collection = {
#             "type": "FeatureCollection",
#             "features": features,
#             }

#         return JsonResponse(feature_collection)
#     else:    
#         return JsonResponse({'error': 'Invalid request'}, status=400)


def load_nuts_polygon(request, entity, polygon_id):
    if request.method == 'GET':
        try:
            # Retrieve the polygon based on the ID
            if entity == 'states':
                polygon = swn_models.NUTS5000_N1.objects.get(id=polygon_id)
            elif entity == 'districts':
                polygon = swn_models.NUTS5000_N2.objects.get(id=polygon_id)
            elif entity == 'counties':
                polygon = swn_models.NUTS5000_N3.objects.get(id=polygon_id)
            

            geojson = json.loads(polygon.geom)

            feature = {
                "type": "Feature",
                "geometry": geojson,
                "properties": {
                    "nuts_name": polygon.nuts_name,
                }
            }
            # print('GeoJSON:', feature)
            return JsonResponse(feature)
        except:
            # Return an error response if the polygon is not found
            error_response = {
                "error": "Polygon not found."
            }
            return JsonResponse(error_response, status=404)
        

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
    
def load_toolbox_project(request, id):

    project = models.ToolboxProject.objects.get(pk=id)
    print("Toolbox Project: ", project)
    if not project:
        return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    else:
        project_json = project.to_json()
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project_json})

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
            geos = GEOSGeometry(body['geom'])
            # geos.transform(25833)
            user = request.user
            instance = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
            instance.save()
            
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
        
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

def get_options(request, parameter):
    dropdown_list = []
    if parameter == 'toolbox-project':
        toolbox_projects = models.ToolboxProject.objects.filter(user=request.user)
        dropdown_list = [(project.id, project.name) for project in toolbox_projects]


    return JsonResponse({'options': dropdown_list})
        

@login_required
def get_field_project_modal(request, id):
    # user_projects = models.SwnProject.objects.filter(Q(user_field__id=id) & Q(user_field_user=request.user))
    user_projects = models.ToolboxProject.objects.filter(Q(user_field__id=id) & Q(user_field__user=request.user))
    print('user_projects:', user_projects)
    print('user_projects.values():', list(user_projects.values()))
    
    return JsonResponse({'projects': list(user_projects.values())})
    
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
    

    
