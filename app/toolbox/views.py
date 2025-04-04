from django.shortcuts import render
from . import models
from swn import models as swn_models
from swn import forms as swn_forms
from . import forms

from django.shortcuts import render, redirect
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


def test(request):
    context = {
        'form': forms.ToolboxProjectForm()
    }
    return render(request, 'toolbox/test.html', context)



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


def filter_sinks(request):
    # TODO enlarged Sinks!
    if request.method == 'POST':
        sink_form = forms.SinksFilterForm(request.POST)
        if sink_form.is_valid():
            sinks = models.Sink.objects.filter(
                depth__gte=sink_form.cleaned_data['depth_min'],
                depth__lte=sink_form.cleaned_data['depth_max'],
                area__gte=sink_form.cleaned_data['area_min'],
                area__lte=sink_form.cleaned_data['area_max'],
                index_soil__gte=sink_form.cleaned_data['index_soil_min'],
                index_soil__lte=sink_form.cleaned_data['index_soil_max'],
            )
            sinks_json = [sink.to_json() for sink in sinks]
            return JsonResponse({'sinks': sinks_json})
        else:
            return JsonResponse({'message': {'success': False, 'message': 'Invalid form data'}})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Invalid request'}})


def load_infiltration_gui(request, user_field_id):
    if user_field_id == "null":
        user_field_id = None
    else:
        user_field_id = int(user_field_id)

        user_field = models.UserField.objects.get(id=user_field_id)
        user_field_geom = GEOSGeometry(user_field.geom)
        sinks = models.Sink4326.objects.filter(
            centroid__within=user_field_geom
        )
        enlarged_sinks = models.EnlargedSink4326.objects.filter(
            centroid__within=user_field_geom
        )
    if user_field_id is not None:
        user_field = models.UserField.objects.get(id=user_field_id)
        user_field_geom = GEOSGeometry(user_field.geom)
        sinks = models.Sink.objects.filter(
            geom__within=user_field_geom
        )
    else:
        sinks = models.Sink.objects.all()

    sink_extremes = sinks.aggregate(
        depth_sink_min=Min('depth'),
        depth_sink_max=Max('depth'),
        area_sink_min=Min('area'),
        area_sink_max=Max('area'),
        volume_min=Min('volume'),
        volume_max=Max('volume'),
    )
    enlarged_sink_extremes = enlarged_sinks.aggregate(
        depth_sink_min=Min('depth'),
        depth_sink_max=Max('depth'),
        area_sink_min=Min('area'),
        area_sink_max=Max('area'),
        volume_min=Min('volume'),
        volume_max=Max('volume'),
    )

    project_select_form = forms.ToolboxProjectSelectionForm()
    sink_form = forms.SinksFilterForm(sink_extremes=sink_extremes)
    enlarged_sink_form = forms.SinksFilterForm(sink_extremes=enlarged_sink_extremes, enlarged_sinks=True)

    lakes = models.Lake.objects.all()
    streams = models.Stream.objects.all()
    lake_extremes = lakes.aggregate(
        min_min_surplus_volume=Min('min_surplus_volume'),
        max_min_surplus_volume=Max('min_surplus_volume'),
        min_mean_surplus_volume=Min('mean_surplus_volume'),
        max_mean_surplus_volume=Max('mean_surplus_volume'),
        min_max_surplus_volume=Min('max_surplus_volume'),
        max_max_surplus_volume=Max('max_surplus_volume'),
        min_plus_days= Min('plus_days'),
        max_plus_days= Max('plus_days'),
    )

    stream_extremes = streams.aggregate(
        min_min_surplus_volume=Min('min_surplus_volume'),
        max_min_surplus_volume=Max('min_surplus_volume'),
        min_mean_surplus_volume=Min('mean_surplus_volume'),
        max_mean_surplus_volume=Max('mean_surplus_volume'),
        min_max_surplus_volume=Min('max_surplus_volume'),
        max_max_surplus_volume=Max('max_surplus_volume'),
        min_plus_days= Min('plus_days'),
        max_plus_days= Max('plus_days'),
    )

    lake_form = forms.WaterbodyFilterForm(extremes=lake_extremes, lake=True)
    stream_form = forms.WaterbodyFilterForm(extremes=stream_extremes)

    lakes = models.Lake4326.objects.all()
    streams = models.Stream4326.objects.all()


    html = render_to_string('toolbox/infiltration.html', {
        'sink_form': sink_form, 
        'enlarged_sink_form': enlarged_sink_form,
        'project_select_form': project_select_form,
        'streams_form': stream_form,
        'lakes_form': lake_form,
    }, request=request) 

    return JsonResponse({'html': html, 'sink_extremes': sink_extremes})

def get_selected_sinks(request):
    if request.method == 'POST':
        try:
            project = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        # print('Project:', type(project), project)
        # print('infiltration:', type(project['infiltration']), project['infiltration'])
        # print('project.userField:', project['userField'])
        user_field = models.UserField.objects.get(pk=project['userField'])
        geom = GEOSGeometry(user_field.geom)
        sinks = []
        if project.get('enlargedSink') is True:
            sinks = models.EnlargedSink4326.objects.filter(geom__within=geom)
            sinks = sinks.filter(
                depth__gte=float(project['infiltration']['enlargedSinkDepthMin']),
                depth__lte=float(project['infiltration']['enlargedSinkDepthMax']),
                area__gte=float(project['infiltration']['enlargedSinkAreaMin']),
                area__lte=float(project['infiltration']['enlargedSinkAreaMax']),
                volume__gte=float(project['infiltration']['enlargedSinkVolumeMin']),
                volume__lte=float(project['infiltration']['enlargedSinkVolumeMax']),
            )
            
        else:
            sinks = models.Sink4326.objects.filter(geom__within=geom)
            sinks = sinks.filter(
                depth__gte=float(project['infiltration']['sinkDepthMin']),
                depth__lte=float(project['infiltration']['sinkDepthMax']),
                area__gte=float(project['infiltration']['sinkAreaMin']),
                area__lte=float(project['infiltration']['sinkAreaMax']),
                volume__gte=float(project['infiltration']['sinkVolumeMin']),
                volume__lte=float(project['infiltration']['sinkVolumeMax']),
            )

        features = []
        for sink in sinks:
            centroid = sink.centroid
            geojson = json.loads(centroid.geojson)
            print('geojson:', geojson)
            geojson['properties'] = {
                "id": sink.id,
                "depth": sink.depth,
                "area": sink.area,
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

        return JsonResponse(feature_collection)
    else:    
        return JsonResponse({'error': 'Invalid request'}, status=400)


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
            print('GeoJSON:', feature)
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
            geos.transform(25833)
            user = request.user
            instance = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
            instance.save()
            
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
        
    else:
        return HttpResponseRedirect('toolbox:toolbox_dashboard')


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
    

    
# def toolbox_get_sinks_within(request, user_field_id):
#     if request.method == 'GET':
#         user_field = models.UserField.objects.get(id=user_field_id)
#         user_field_geom = GEOSGeometry(user_field.geom)
#         sinks = models.Sink4326.objects.filter(
#             geom__within=user_field_geom
#         )
#         enlarged_sinks = models.EnlargedSink4326.objects.filter(
#         geom__within=user_field_geom
#         )
#         sinks_json = [sink.to_json() for sink in sinks]
#         enlarged_sinks_json = [sink.to_json() for sink in enlarged_sinks]
#         return JsonResponse({'sinks': sinks_json, 'enlarged_sinks': enlarged_sinks_json})
#     else:
#         return JsonResponse({'message': {'success': False, 'message': 'Invalid request'}})
    

# def toolbox_get_sinks_within(request, user_field_id):
#     user_field = swn_models.UserField.objects.get(id=area_id)
#     # user_field_geom = GEOSGeometry(user_field.geom)
#     sinks = models.SinksWithLandUseAndSoilPropertiesAsPoints.objects.filter(
#         geom__within=user_field.geom
#     )
#     features = []
#     # print(sinks)
#     for sink in sinks:
#         geometry = GEOSGeometry(sink.geom)
        
#         geojson = json.loads(geometry.geojson)
#         geojson['properties'] = {
#             "Tiefe": sink.depth_sink,
#             "Fläche": sink.area_sink,
#             "Eignung": str(sink.index_sink * 100) + "%",
#             "Eignung 2": str(sink.index_si_1 * 100) + "%",
#             "Landnuntzung 1": sink.landuse_1,
#             "Landnuntzung 2": sink.landuse_2,
#             "Landnuntzung 3": sink.landuse_3,
#             "Bodenindex": sink.index_soil ,
#         }
#         features.append(geojson)
#     feature_collection = {
#         "type": "FeatureCollection",
#         "features": features,
#         }
    
    # soils = models.SoilProperties4326.objects.objects.filter(
    #     geom__within=user_field_geom
    # )
    # index_soil = sinks.values_list('index_soil', flat=True).distinct()
    # Return the GeoJSON FeatureCollection as a JSON response
    return JsonResponse(feature_collection)