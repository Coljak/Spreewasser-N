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

# an alternative could be https://github.com/smlum/netcdf-vis

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


def get_timeseries_data(request):
    start = datetime.now()
    params = request.GET.dict()

    p = {
        'layers': 'hurs',
        'start_time': '2011-01-01',
        'end_time': '2011-12-04',
        'lat_lon': '50.986099,11.975098',
    }
    lat = p['lat_lon'].split(',')[0]
    lon = p['lat_lon'].split(',')[1]
    lat_2 = float(lat) + 0.1
    lon_2 = float(lon) + 0.1
    bbox = f'{lat},{lon},{lat_2},{lon_2}'

    params = {
        'version': '1.3.0',
        'request':'GetTimeseries',
        'layers': p['layers'],
        'styles': 'default',
        'crs': 'EPSG:4326',
        'BBOX': bbox,
        'WIDTH': '1',
        'HEIGHT': '1',
        # 'format': 'image/png',
        'info_format': 'text/json',
        'query_layers': p['layers'],
        'TIME': p['start_time'] + '/' + p['end_time'],
        'i': 0,
        'j': 0
    }
    netcdf = 'zalf_hurs_amber_2011_v1-0_cf_v6.nc'
    url = 'http://thredds:8080/thredds/wms/data/DWD_Data/' + netcdf
    response = requests.get(url, params=params)
    layer = p['layers']
    response_json = response.json()
    # the loop is a little one second faster than the conversion to a numpy array
    formatted_dates = [datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d-%m-%Y') for date_string in response_json['domain']['axes']['t']['values']]

    # dates = np.array(response_json['domain']['axes']['t']['values']),
    # # Vectorize the conversion function
    # convert_to_datetime_vec = np.vectorize(convert_to_datetime)


    # # Convert the date strings to datetime objects and format them as dd-mm-yyyy
    # formatted_dates = convert_to_datetime_vec(dates)
    values = response_json['ranges'][layer]['values']
    chart_data = {
                'Date': formatted_dates,
                layer: values, 
                'max': max([max(values)]),     
            }
    print('chart_data', chart_data)

    response.raise_for_status()
    end = datetime.now()
    print('Time to get timeseries data:', end - start)
    return JsonResponse(chart_data)


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

def register(request):

    registered = False

    if request.method == "POST":
        
        user_form = forms.UserForm(data=request.POST)
        # profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid():  # and profile_form.is_valid():
          
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
            return redirect('swn:user_login')
        else:
            print("userForm NOT valid")
            print(user_form.errors)

    else:
        user_form = forms.UserForm()

    return render(request, 'swn/registration.html',
                  {'user_form': user_form,
                   # 'pk': user.id,
                   'registered': registered})

def user_login(request):
    print("USER_LOGIN")
    if request.method == "POST":
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, name=username, password=password)
        # if '@' in username:
        #     email = username
        #     user = authenticate(email=email, password=password)
        # else:
        #     user = authenticate(name=username, password=password)
        #user = authenticate(email=email, password=password)
        if user:
            if user.is_active:

                login(request, user)
                initial = user.username
                return HttpResponseRedirect(reverse('swn:swn_user_dashboard'))

            else:
                return HttpResponse("Account is not active!")
            
        # TODO make this go to handle alerts
        else:
            return JsonResponse({'alert': "the login failed"})

    else:
        login_form = forms.LoginForm()
        return render(request, 'swn/login.html', {'login_form': login_form})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('swn:swn_index'))



def three_split(request):
    print("Request.user", request.user)
    user = request.user
    user_fields = models.UserField.objects.filter(user=request.user.id)
    context = monica_views.get_monica_forms(user)


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
    
    # MONICA forms etc (from Monica.views)
    # coordinate_form = monica_forms.CoordinateForm()
    user_field_selector_form = forms.UserFieldSelectorForm(user=user)

    project_select_form = forms.SwnProjectSelectionForm(user=user)
    project_form = forms.SwnProjectForm(user=user)
    project_modal_title = 'Create new project'

    coordinate_form = monica_forms.CoordinateForm()
   

    # user_simulation_settings = monica_models.UserSimulationSettings.objects.get(is_default=True)
    # user_simulation_settings_form = monica_forms.UserSimulationSettingsForm(instance=user_simulation_settings)

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
            'user_field_form': forms.UserFieldForm(),
            'state_county_district_form': state_county_district_form,
            'project_region': feature,
            #MONICA FORMS
            'project_select_form': project_select_form,
            'project_form': project_form,
            'project_modal_title': project_modal_title,
            'coordinate_form': coordinate_form,
            'user_field_selector_form': user_field_selector_form,
            'user_crop_parameters_select_form': user_crop_parameters_select_form,
            # 'user_crop_parameters_form': user_crop_parameters_form,
            'user_simulation_settings_select_form': user_simulation_settings_select_form,
            # 'simulation_settings_form': user_simulation_settings_form,
            'user_environment_parameters_select_form': user_environment_parameters_select_form,
            # 'user_environment_parameters_form': user_environment_parameters_form,

            'user_soil_moisture_select_form': user_soil_moisture_select_form,
            'user_soil_organic_select_form': user_soil_organic_select_form,
            'soil_temperature_module_selection_form': soil_temperature_module_select_form, 
            'user_soil_transport_parameters_selection_form': user_soil_transport_parameters_select_form,
            }
    
    context.update(data)
    return render(request, 'swn/swn_three_split.html', context)


def load_projectregion(request):
    projectregion = models.ProjectRegion.objects.first()
    geojson = json.loads(projectregion.geom.geojson) 
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }
    return JsonResponse(feature)


# def get_user_fields(request):
#     if request.method == "GET":

#         # user_projects = models.UserProject.objects.filter(user_field__user=request.user)
#         user_fields = models.UserField.objects.filter(user=request.user)
#         user_projects = models.UserProject.objects.filter(user=request.user)

#     return JsonResponse({'user_fields': list(user_fields.values('id', 'user', 'name', 'geom_json'))})

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
        print('user_fields:', ufs)
    return JsonResponse({'user_fields': ufs})

@login_required
def update_user_field(request, pk):
    obj = models.UserField.objects.get(pk=pk)
    if is_ajax(request):

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
            instance.save()

            instance.get_intersecting_soil_data()
            instance.get_weather_grid_points()
            
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
        
    else:
        return HttpResponseRedirect('swn:swn_user_dashboard')

@login_required
@csrf_protect
# @action_permission
def delete_user_field(request, id):
    print("request in views:", request.user)
    if is_ajax(request):
        print("Save IS AJAX")
        form = forms.UserFieldForm(request.POST or None)
        name = request.POST.get('id')
        user_id = request.user.id
        user_field = models.UserField.objects.get(id=id, user_id = user_id)
        user_field.delete()
        
        return JsonResponse({})
    return redirect('swn:swn_user_dashboard')

@login_required
def get_field_project(request, id):
    user_projects = models.UserProject.objects.filter(Q(user_field_id=id) & Q(user_field_user=request.user))
    
    return JsonResponse({'user_project': list(user_projects.values())})


def load_nuts_polygon(request, entity, polygon_id):
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


def sidebar_working(request):
    return render(request, 'swn/sidebar_copied_working.html')

def sidebar_not_working(request):
    return render(request, 'swn/sidebar_copied_not_working.html')

def get_centroid(request, user_field_id):
    lon, lat = models.UserField.objects.get(id=user_field_id).get_centroid()

    return JsonResponse({'lon': lon, 'lat': lat})



def load_swn_project(request, id):
    try:
        project = models.SwnProject.objects.get(pk=id)
        return JsonResponse({'message':{'success': True, 'message': f'Project {project.name} loaded'}, 'project': project.to_json()})
    except:
            return JsonResponse({'message':{'success': False, 'message': 'Project not found'}})
    

def save_swn_project(request, project_id=None):
    print("CREATE SWN PROJECT\n", request.POST)

    project = save_monica_project.save_project(request, project_class=models.SwnProject, project_id=project_id, additional_fields=True)

    return JsonResponse({
        'message': {
            'success': True, 
            'message': f'Project {project.name} saved'
            }, 
            'project_id': project.id, 
            'project_name': project.name
            })

def get_parameter_options(request, parameter_type, id=None):
    """
    Get choices for select boxes- those that occur ONLY in SWN.
    """
    user = request.user.id
    print("GET PARAMETER OPTIONS from SWN: ", parameter_type, id,)

    if parameter_type == 'monica-project':
         options = models.SwnProject.objects.filter(Q(user=None) | Q(user=user)).values('id', 'name')
    else:
        options = []

    return JsonResponse({'options': list(options)})

