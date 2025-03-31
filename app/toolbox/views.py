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
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db.models import F, Q

from django.contrib.gis.db.models import PointField
from django.db import connection
# Create your views here.


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
    

    
def toolbox_get_sinks_within(request, user_field_id):
    if request.method == 'GET':
        user_field = models.UserField.objects.get(id=user_field_id)
        user_field_geom = GEOSGeometry(user_field.geom)
        sinks = models.Sink4326.objects.filter(
        geom__within=user_field_geom
        )
        sinks_json = [sink.to_json() for sink in sinks]
        return JsonResponse({'sinks': sinks_json})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Invalid request'}})
    

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