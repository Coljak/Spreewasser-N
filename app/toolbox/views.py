from django.shortcuts import render
from . import models
from swn import models as swn_models
from . import forms

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.serializers import serialize
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from django.db.models import F, Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models import PointField
from django.db import connection
# Create your views here.


def toolbox_dashboard(request):

    projectregion = swn_models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }
    
    context = {
        'project_region': feature,
    }

    return render(request, 'toolbox/toolbox_three_split.html', context)



def load_nuts_polygon(request, entity, polygon_id):
    if request.method == 'GET':
        try:
            # Retrieve the polygon based on the ID
            if entity == 'states':
                polygon = models.NUTS5000_N1.objects.get(id=polygon_id)
            elif entity == 'districts':
                polygon = models.NUTS5000_N2.objects.get(id=polygon_id)
            elif entity == 'counties':
                polygon = models.NUTS5000_N3.objects.get(id=polygon_id)
            
            # Generate the GeoJSON representation of the polygon
            geometry = GEOSGeometry(polygon.geom)
            geojson = json.loads(geometry.geojson)

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
    print("CREATE SWN PROJECT\n", request.POST)
    if request.method == 'POST':
        user = request.user
        
        project_data = json.loads(request.body)
        project = models.ToolboxProject.objects.create(
            name=project_data['name'],
            user=user,
            project_data=project_data
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
            geos = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            instance = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
            # TODO this should rather be a save method of UserField
            instance.save()
            instance.get_centroid()
            instance.get_intersecting_soil_data()
            instance.get_weather_grid_points()
            
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
        
    else:
        return HttpResponseRedirect('swn:swn_dashboard')
    
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
    

    

def get_user_fields(request):
    if request.method == "GET":
        user_fields = models.UserField.objects.filter(user=request.user)
        user_projects = models.SwnProject.objects.filter(user=request.user)
        ufs = []
        for user_field in user_fields:
            uf = model_to_dict(user_field, fields=['id', 'user', 'name', 'geom_json'])
            uf['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
        # print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})