import json, asyncio, csv
from django.middleware import csrf
from multiprocessing import managers
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from django.forms.models import model_to_dict
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.conf import settings
import numpy as np
import requests
from . import forms
from . import models
from monica.utils import save_monica_project

from monica import forms as monica_forms
from monica import models as monica_models
from monica import views as monica_views

from buek import models as buek_models
from toolbox import models as toolbox_models
from app.helpers import is_ajax
import xmltodict
from datetime import datetime, timedelta
import copy

from .utils import get_geolocation
import random

from .data import calc_list, calc_dict
from datetime import date
import time
import urllib
# from bs4 import BeautifulSoup

# dev feature displays all bootstrap colors etc.
def bootstrap(request):
    return render(request, 'swn/bootstrap_colors.html')

# helper function to convert np arrays of date strings 
def convert_to_datetime(date_string):
    return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d-%m-%Y')

def get_csrf_token(request):
    data = {
        'csrfToken': csrf.get_token(request)
    }
    return JsonResponse(data)



class IndexView(TemplateView):
    template_name = "swn/home.html"

class ImpressumView(TemplateView):
    template_name = "swn/impressum_information.html"

class AcknoledgementsView(TemplateView):
    template_name = "swn/acknoledgements.html"

# turning off the default browser favicon request
def favicon_view(request):
    return HttpResponse(status=204)

# This view outputs a json file containing a list of jsons of all available datasets on the thredds server
def thredds_catalog(request):
    url = 'http://thredds:8080/thredds/catalog/data/DWD_Data/catalog.xml'

    response = requests.get(url)
    catalog_dict = xmltodict.parse(response.content)

    # thredds content as dataset from list comprehension
    catalog_dict_list = [
        {
            "name": dataset['@name'],
            "urlPath": dataset['@urlPath'],
            "size": f"{dataset['dataSize']['#text']} {dataset['dataSize']['@units']}",
            "date_modified": (
                datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if '.' in dataset['date']['#text']
                else datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%SZ")
            ).strftime("%d-%m-%Y"),
        }
        for dataset in catalog_dict['catalog']['dataset']['dataset']
    ]

    return render(request, 'swn/thredds_catalog.html', {'catalog_json': catalog_dict_list})



def get_wms_capabilities(request, name):
    url = "http://thredds:8080/thredds/wms/data/DWD_Data/" + name
    params = {
        'service': 'WMS',
        'version': '1.3.0',
        'request': 'GetCapabilities', 
    }
    response = requests.get(url, params=params)
    return HttpResponse(response)

def get_ncml_metadata(request, name):
    url = "http://thredds:8080/thredds/ncml/data/DWD_Data/" + name
    nc_dict = {}
    ncml = requests.get(url)
    ncml_data = xmltodict.parse(ncml.text)
    try:
        nc_dict['global_attributes'] = {}
        for attr in ncml_data['netcdf']['attribute']:
            nc_dict['global_attributes'][attr['@name']] = attr['@value']

        nc_dict['dimensions'] = {}
        for var in ncml_data['netcdf']['dimension']:
            nc_dict['dimensions'][var['@name']] = {'length': var['@length']}
            if '@isUnlimited' in var.keys():
                nc_dict['dimensions'][var['@name']]['isUnlimited'] = var['@isUnlimited']

        nc_dict['variables'] = {}
        for var in ncml_data['netcdf']['variable']:
            nc_dict['variables'][var['@name']] = {'shape': var['@shape'], 'type': var['@type'], 'attributes': {}}
            for att in var['attribute']:  
                nc_dict['variables'][var['@name']]['attributes'][att['@name']] = att['@value']
    except:
        nc_dict = {'error': 'No metadata available'}

    data = {}
    data['title'] = nc_dict['global_attributes']['title']
    data['variable'] = [x for x in list(nc_dict['variables'].keys()) if x not in list(nc_dict['dimensions'].keys())]
    time_coverage_start = nc_dict['global_attributes']['time_coverage_start']
    
    start_date = datetime.strptime(time_coverage_start, "%Y-%m-%d %H:%M:%SA")
    time_coverage_start = start_date.strftime("%Y-%m-%d")
    data['time_coverage_start'] = time_coverage_start
    new_date = start_date + timedelta(days=int(nc_dict['dimensions']['time']['length']))
    data['time_coverage_end'] = new_date.strftime("%Y-%m-%d")
    nc_dict['global_attributes']['time_coverage_start_ymd'] = time_coverage_start
    nc_dict['global_attributes']['time_coverage_end_ymd'] = new_date.strftime("%Y-%m-%d")

    # print('data', data)         

    return JsonResponse(nc_dict)


# This view outputs a json containing all relevant attributes of a netcdf file
def get_ncml_capabilities_2(request, name):
    print('{\n get_wms_capabilities \n', name)
    url = 'http://thredds:8080/thredds/ncml/data/DWD_Data/' + name
   
    response = requests.get(url)
    catalog_dict = xmltodict.parse(response.content)

    capabilities = {} # important ones: title, time_coverage_start 
    global_attributes = {}

             
    # for the ncml method
    for item in catalog_dict["netcdf"]["attribute"]:
        global_attributes[item['@name']] = item['@value']
    capabilities['global_attributes'] = global_attributes

    capabilities['attributes'] = {}
    for attr in catalog_dict["netcdf"]["attribute"]:
        
        capabilities['attributes'][attr['@name']] = attr['@value']
    capabilities['dimensions'] = {}
    for dim in catalog_dict["netcdf"]["dimension"]:
        
        capabilities['dimensions'][dim['@name']] = {'length': dim['@length'], 'isUnlimited': dim['@isUnlimited'] if '@isUnlimited' in dim.keys() else "false"}

    capabilities['groups'] = {}
    for group in catalog_dict["netcdf"]["group"]:
        capabilities['groups'][group['@name']] = {}
        for attr in group["attribute"]:
            capabilities['groups'][group['@name']][attr['@name']] = attr['@value']

    capabilities['variables'] = {}
    for variable in catalog_dict["netcdf"]["variable"]:
        
        capabilities['variables'][variable['@name']] = {}
        capabilities['variables'][variable['@name']]['shape'] = variable['@shape']
        capabilities['variables'][variable['@name']]['type'] = variable['@type']
        for attr in variable['attribute']:
            capabilities['variables'][variable['@name']][attr['@name']] = attr['@value']
        
    print("capabilities", capabilities)
    # return JsonResponse(catalog_dict)
    return JsonResponse(capabilities)
    
# This view outputs a json containing all relevant catalog infos of all netcdf files and renders the HTML template
def timelapse_items(request):
    # List of datasaet as in the thredds_catalog view
    url = 'http://thredds:8080/thredds/catalog/data/DWD_Data/catalog.xml'

    response = requests.get(url)
    catalog_dict = xmltodict.parse(response.content)
    print("\nSWN catalog_dict['catalog']['dataset']['dataset']\n", catalog_dict['catalog']['dataset']['dataset'])
    # thredds content as dataset from list comprehension
    catalog_dict_list = [
        {
            "name": dataset['@name'],
            "urlPath": dataset['@urlPath'],
            "size": f"{dataset['dataSize']['#text']} {dataset['dataSize']['@units']}",
            "date_modified": (
                datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%S.%fZ")
                if '.' in dataset['date']['#text']
                else datetime.strptime(dataset['date']['#text'], "%Y-%m-%dT%H:%M:%SZ")
            ).strftime("%d-%m-%Y"),
        }
        for dataset in catalog_dict['catalog']['dataset']['dataset']
    ]

    return render(request, 'swn/map_thredds_4.html', {'catalog_json': catalog_dict_list, 'thredds_data': 'thredds_data'})

def timelapse_test_django_passthrough_wms(request, netcdf):

    print("timelapse_test_django_passthrough_wms", netcdf)
    url = 'http://thredds:8080/thredds/wms/data/DWD_Data/' + netcdf
    
    params = request.GET.dict()
    # Timeseries legend image
    
    # Timeseries WMS
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Return the response content to the frontend
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        # Handle request exception, e.g., log the error
        return HttpResponse(f"Error: {e}", content_type='text/plain')

def sign_up(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('swn:swn_user_dashboard')
    else:
        form = forms.RegistrationForm()

    return render(request, 'registration/sign_up.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('swn:swn_index'))

def three_split(request):
    print("Request.user", request.user)
    user = request.user
    user_fields = models.UserField.objects.filter(user=request.user.id)
    context = monica_views.get_monica_forms(user)

    default_project = monica_views.create_default_project(user)


    state_county_district_form = forms.PolygonSelectionForm(request.POST or None)
    
    projectregion = models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }

    project_select_form = forms.SwnProjectSelectionForm(user=user)
    project_form = forms.SwnProjectForm(user=user)
    project_modal_title = 'Create new project'

    coordinate_form = monica_forms.CoordinateForm()
   
    user_simulation_settings_select_form = monica_forms.UserSimulationSettingsInstanceSelectionForm(user=user)

    user_crop_parameters_select_form = monica_forms.UserCropParametersSelectionForm(user=user)
    # user_crop_parameters_form = monica_forms.UserCropParametersForm()

    user_environment_parameters_select_form = monica_forms.UserEnvironmentParametersSelectionForm(user=user)
    # user_environment_parameters_form = monica_forms.UserEnvironmentParametersForm(user=user)

    user_soil_moisture_select_form = monica_forms.UserSoilMoistureInstanceSelectionForm(user=user)
    user_soil_organic_select_form = monica_forms.UserSoilOrganicInstanceSelectionForm(user=user)
    soil_temperature_module_select_form = monica_forms.SoilTemperatureModuleInstanceSelectionForm(user=user)
    user_soil_transport_parameters_select_form = monica_forms.UserSoilTransportParametersInstanceSelectionForm(user=user)

    data = {
            # 'user_fields': user_projects, 
            'default_project': default_project,
            'user_field_form': forms.UserFieldForm(),
            'state_county_district_form': state_county_district_form,
            'project_region': feature,
            #MONICA FORMS
            'project_select_form': project_select_form,
            'project_form': project_form,
            'project_modal_title': project_modal_title,
            'coordinate_form': coordinate_form,
            'user_crop_parameters_select_form': user_crop_parameters_select_form,
            'user_simulation_settings_select_form': user_simulation_settings_select_form,
            'user_environment_parameters_select_form': user_environment_parameters_select_form,
            'user_soil_moisture_select_form': user_soil_moisture_select_form,
            'user_soil_organic_select_form': user_soil_organic_select_form,
            'soil_temperature_module_selection_form': soil_temperature_module_select_form, 
            'user_soil_transport_parameters_selection_form': user_soil_transport_parameters_select_form,
            }
    
    context.update(data)
    return render(request, 'swn/swn_three_split.html', context)



def get_user_fields(request):
    if request.method == "GET":

        # user_projects = models.UserProject.objects.filter(user_field__user=request.user)
        user_fields = models.UserField.objects.filter(user=request.user)
        user_projects = models.SwnProject.objects.filter(user=request.user)
        ufs = []
        for user_field in user_fields:
            uf = model_to_dict(user_field, fields=['id', 'user', 'name', 'geom_json'])
            uf['user_projects'] = list(user_projects.filter(user_field=user_field).values('id', 'name', 'creation_date', 'last_modified'))
            ufs.append(uf)
        # print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})

@login_required
def update_user_field(request, pk):
    """
    Currently not in use!
    """
    obj = models.UserField.objects.get(pk=pk)

    if request.POST and request.user.is_authenticated:

        obj.name = request.POST.get('name')
        obj.geom_json = request.POST.get('geomJson')
        obj.geom = request.POST.get('geom')


        obj.save()
        return JsonResponse({
            'fieldName': obj.name,
            'geom': obj.geom,
        })
    return redirect('swn:swn_user_dashboard')

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
        return HttpResponseRedirect('swn:swn_user_dashboard')
    

@login_required
@csrf_protect
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
def get_field_project(request, id):
    user_projects = models.UserProject.objects.filter(Q(user_field_id=id) & Q(user_field_user=request.user))
    
    return JsonResponse({'user_project': list(user_projects.values())})


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


def manual_soil_selection(request, user_field_id):
    print("field_menu id: ", id)
    
    start_time = time.time()

    user_field = models.UserField.objects.get(id=user_field_id)
    soil_profile_polygon_ids = user_field.soil_profile_polygon_ids['buek_polygon_ids']

    name = user_field.name
    data_menu = monica_views.soil_profiles_from_polygon_ids(user_field.soil_profile_polygon_ids['buek_polygon_ids'])
    data_menu['text'] = name
    data_menu['id'] = user_field.id

    print('elapsed_time for soil json', (start_time - time.time()), ' seconds')
    return render(request, 'monica/modal_manual_soil_selection.html', data_menu)


def load_swn_project(request, id):
    try:
        project = models.SwnProject.objects.get(pk=id)
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project.to_json()})
    except:
            return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    

def save_swn_project(request, project_id=None):
    print("CREATE SWN PROJECT\n", request.POST)
    if request.method == 'POST':
        user = request.user
        
        project_data = json.loads(request.body)
        project = save_monica_project.save_project(project_data, user, project_class=models.SwnProject)

        return JsonResponse({
            'message': {
                'success': True, 
                'message': f'Project {project.name} saved'
                }, 
                'project_id': project.id, 
                'project_name': project.name
                })
    
def create_regular_irrigation_envs(envs, data):
    """
    This function creates a new environment for each irrigation event.
    Irrigations sets the interval in days and amount of irrigation in millimeters.
    """
    today = datetime.strptime(data.get('todaysDate').split('T')[0], '%Y-%m-%d')
    # irrigations = [(3, 10.0), (3, 20.0), (6, 10.0), (6, 20.0), (9, 30.0)]
    irrigations = [ (6, 10.0), (6, 20.0), (9, 30.0)]
    for days, amount in irrigations:
        date = copy.deepcopy(today)
        env2 = copy.deepcopy(envs[0])
        worksteps = env2['cropRotation'][-1].get('worksteps')
        while date <= datetime.strptime(data.get('endDate').split('T')[0], '%Y-%m-%d'):
            date += timedelta(days=days)
            worksteps.append({
                "type": "Irrigation",
                "date": date.strftime('%Y-%m-%d'),
                "amount": [amount, 'mm']
            })
        worksteps.sort(key=lambda x: x['date'])
        env2['cropRotation'][-1]['worksteps'] = worksteps
        envs.append(env2)
    return envs

def create_automatic_irrigation_envs(envs, data):
    """
    This function creates a new environment for each automatic irrigation event.
    """
    # today = datetime.strptime(data.get('todaysDate').split('T')[0], '%Y-%m-%d')
    today = data.get('todaysDate').split('T')[0]
    print("CREATING EXTRA ENV", today)

    simulation_settings = [
        # UserSimulationSettings.objects.get(id=30).to_json(),
        monica_models.UserSimulationSettings.objects.get(id=31).to_json(),
        monica_models.UserSimulationSettings.objects.get(id=32).to_json()
    ]
    for sim in simulation_settings:
        # sim["AutoIrrigationParams"]["startDate"] = today.strftime('%Y-%m-%d')
        sim["AutoIrrigationParams"]["startDate"] = today
        env2 = copy.deepcopy(envs[0])
        env2["params"]["simulationParameters"] = sim
        envs.append(env2)

    return envs
    
def run_simulation(request):
    # TODO projectId!!!!
    user = request.user

    if request.method == 'POST':
        # data is the project json
        data = json.loads(request.body)
        print("Saving Project\n", data)
        try:
            if data.get('id'):
                project = save_monica_project.save_project(data, user,  project_class=models.SwnProject)
        except:
            pass

        print("Simulation is starting...\n")
        
        
        env = monica_views.create_monica_env_from_json(data)
        # # split function here --> if swn, then create irrigation
        envs = [env]
        
        
        envs = create_automatic_irrigation_envs(envs, data)
        json_msgs = monica_views.run_monica_simulation(envs)
        
        return JsonResponse({'message': {'success': True, 'message': json_msgs}})
    else:
        return JsonResponse({'message': {'success': False, 'message': 'Simulation not started.'}})

def get_parameter_options(request, parameter_type, id=None):
    """
    Get choices for select boxes- those that occur ONLY in SWN.
    For all others there is a function get_parameter_options in monica.views.
    """
    user = request.user.id
    print("GET PARAMETER OPTIONS from SWN: ", parameter_type, id,)

    if parameter_type == 'monica-project':
         options = models.SwnProject.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    else:
        options = []

    return JsonResponse({'options': list(options)})


