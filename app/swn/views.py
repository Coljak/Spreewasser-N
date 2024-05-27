import json, asyncio, csv
from django.middleware import csrf
from multiprocessing import managers
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, HttpResponseBadRequest, JsonResponse
from importlib.util import spec_from_file_location
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.conf import settings
import numpy as np
import requests
from . import forms
from monica import forms as monica_forms
from . import models

from toolbox import models as toolbox_models
from app.helpers import is_ajax
import xmltodict
from datetime import datetime, timedelta

# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic

from .utils import get_geolocation
import random

from .data import calc_list, calc_dict
from datetime import date
import time
import urllib
from bs4 import BeautifulSoup


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

# this renders the example for the NetCDF timelapse from https://github.com/socib/Leaflet.TimeDimension
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

def get_wms_capabilities_json(request, name):
    url = "http://thredds:8080/thredds/wms/data/DWD_Data/" + name
    params = {
        'service': 'WMS',
        'version': '1.3.0',
        'request': 'GetCapabilities', 
    }
    response = requests.get(url, params=params)
    response_json = xmltodict.parse(response.content)
    print('json_response', response_json)
    return JsonResponse(response_json)

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
        # if attr['@name'] == 'title':
        #     capabilities['title'] = attr['@value']
        # elif attr['@name'] == 'time_coverage_start':
        #     capabilities['time_coverage_start'] = attr['@value']
        # elif attr['@name'] == 'time_coverage_end':
        #     capabilities['time_coverage_end'] = attr['@value']
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
    # example netcdf from frontend: zalf_pr_amber_2009_v1-0_cf_v4.nc 

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
            return redirect('swn:user_dashboard')
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
                return HttpResponseRedirect(reverse('swn:user_dashboard'))

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

@login_required
def user_dashboard(request):

    drought_vars = {
        'header': 'Dürrevorhersage',
        'overlays': [
            {
                'name': 'Digitales Höhenmodell',
                'url': 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/hydrodynamics/wave/model_run_aggregation/ww3_med_iberia_latest.nc',
                'layers': 'hs',
                'format': 'image/png',
                'transparent': True,
                'opacity': 0.5,
                'zIndex': 5,
                'bounds': [[47.136744752, 15.57241882], [55.058996788, 5.564783468]],
            },
            {
                'name': 'Dürreindex',
                'url': 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/hydrodynamics/wave/model_run_aggregation/ww3_med_iberia_latest.nc',
                'layers': 'tp',
                'format': 'image/png',
                'transparent': True,
                'opacity': 0.5,
                'zIndex': 5,
                'bounds': [[46.89, 15.33], [55.31, 5.41]]
            },
            {
                'name': 'Temperatur',
                'url': 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/hydrodynamics/wave/model_run_aggregation/ww3_med_iberia_latest.nc',
                'layers': 't02',
                'format': 'image/png',
                'transparent': True,
                'opacity': 0.5,
                'zIndex': 5,
            },
            {
                'name': 'Wind',
                'url': 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/hydrodynamics/wave/model_run_aggregation/ww3_med_iberia_latest.nc',
                'layers': 'wind',
                'format': 'image/png',
                'transparent': True,
                'opacity': 0.5,
                'zIndex': 5,
            },
        ]
        
    }

    above_ground_waters = toolbox_models.AboveGroundWaters.objects.all()
    below_ground_waters = toolbox_models.BelowGroundWaters.objects.all()

    toolbox_vars = {
        'header': 'Toolbox ',
        'overlays': [
            {
                'name': 'Digitales Höhenmodell',

            }
        ]
    }


    user_fields = models.UserProject.objects.filter(user_field__user=request.user)
    # name_form = forms.UserFieldForm(request.POST or None)
    # projects_json = serialize('json', projects)
    crop_form = forms.CropForm(request.POST or None)
    project_form = forms.UserProjectForm()
    field_name_form = forms.UserFieldForm()
    user_projects = []

    for user_field in user_fields:
        if request.user == user_field.field.user:
            item = {
                'name': user_field.name,
                'user_name': user_field.field.user.name,
                'field': user_field.field.name,
                'irrigation_input': user_field.irrigation_input,
                'irrigation_output': user_field.irrigation_output,

                'field_id': user_field.field.id,
                'monica_calculation': user_field.calculation,
            }
            user_projects.append(item)



    # state, county and district choices

    state_county_district_form = forms.PolygonSelectionForm(request.POST or None)

    if state_county_district_form.is_valid():
        selected_states = state_county_district_form.cleaned_data['states']
        selected_counties = state_county_district_form.cleaned_data['counties']
        selected_districts = state_county_district_form.cleaned_data['districts']
        
        # Process the selected polygons and pass the data to the map template


    data = {
            'user_projects': user_projects, 
            'user_field_form': field_name_form,
            'crop_form': crop_form, 
            'project_form': project_form,
            'state_county_district_form': state_county_district_form,
            }


    return render(request, 'swn/user_dashboard.html', data)


def load_projectregion(request):
    projectregion = models.ProjectRegion.objects.all()
    geometry = GEOSGeometry(projectregion[0].geom)
    geojson = json.loads(geometry.geojson)
    feature = {
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "name": 'Spreewasser:N Projektregion',
            }
        }
    return JsonResponse(feature)


def get_chart(request, field_id, crop_id, soil_id):
    print('Request:', crop_id)
    key = ''
    if crop_id == 0:
        key = 'winterwheat'
    elif crop_id == 1:
        key = 'winterbarley'
    elif crop_id == 2:
        key = 'winterrape'
    elif crop_id == 3:
        key = 'winterrye'
    elif crop_id == 4:
        key = 'potato'
    elif crop_id == 5:
        key = 'silage_maize'
    elif crop_id == 6:
        key = 'springbarley'
    print(key)

    # soil_profile = models.BuekSoilProfileHorizon.objects.select_related('bueksoilprofile').filter(
    #         bueksoilprofile__id=soil_id
    #         ).order_by('horizont_nr')
    # key_list = ['winterwheat', 'winterbarley', 'winterrape', 'winterrye', 'potato', 'silage_maize', 'springbarley', ]
    if is_ajax(request):

        calc = calc_dict[key]
        # calc = calc_list[rand]
        response = {
            'mois_max': max([max(calc['Mois_1']), max(calc['Mois_2']), max(calc['Mois_3'])]),
            'lai_max': max(calc['LAI']),
            'Date': calc['Date'],
            'Mois_1': calc['Mois_1'],
            'Mois_2': calc['Mois_2'],
            'Mois_3': calc['Mois_3'],
            'LAI': calc['LAI'],
            
        }
        print('get_chart Jsonresponse \n', JsonResponse(response))

    return JsonResponse(response)


def get_user_fields(request):
    if request.method == "GET":
        print("GET, headers:", request.headers)
        print("GET, body:", request.body)
        user_projects = models.UserProject.objects.filter(user_field__user=request.user)
        user_fields = models.UserField.objects.filter(user=request.user)
    else:
        user_projects = models.UserProject.objects.filter(
            field__user=request.user)
        user_fields = models.UserField.objects.filter(user=request.user)

        # Toolbox Projects
        toolbox_projects = toolbox_models.UserProject.objects.filter(user=request.user)
        print('toolbox_projects', toolbox_projects)

    return JsonResponse({'user_fields': list(user_fields.values('id', 'user', 'name', 'geom_json', 'swn_tool')), 'user_projects': list(user_projects.values())})

@login_required
def update_user_field(request, pk):
    obj = models.UserField.objects.get(pk=pk)
    if is_ajax(request):

        obj.name = request.POST.get('name')
        obj.geom_json = request.POST.get('geomJson')
        obj.geom = request.POST.get('geom')
        obj.swn_tool = request.POST.get('swnTool')

        obj.save()
        return JsonResponse({
            'fieldName': obj.name,
            'geom': obj.geom,
        })
    return redirect('swn:user_dashboard')

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
            swn_tool = body['swnTool']
            geom = json.loads(body['geom'])
            geos = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            instance = models.UserField(name=name, swn_tool=swn_tool, geom_json=geom, geom=geos, user=user)
            instance.save()
            if swn_tool == 'drought':
                instance.get_intersecting_soil_data()
                instance.get_weather_data()
            
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id, 'swn_tool': instance.swn_tool})
        
    else:
        return HttpResponseRedirect('swn:user_dashboard')

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
    return redirect('swn:user_dashboard')


"""
This is for an overview, what is on the thredds server. It cannot yet be used to access the data.
TODO: make it possible to access the data by accessing the xmls on the server,extracting necessary information.
The THREDDS Server is not open for direct access to limit security risks.
"""  

# def thredds_wms_view(request, **args):
#     print("\nNew call of thredds_wms_view \n")
#     thredds_catalog_url = 'http://thredds:8080/thredds/'
#     print("args: ", args)

#     if args == {}:
#             thredds_catalog_url = thredds_catalog_url + 'catalog/catalog.html'
#     elif args['thredds_link'].split('/')[-1].split('.')[-1] not in ('html', 'nc', 'ncd', 'ncml', 'xml'):
#         return HttpResponse()
#     elif args['thredds_link'] == 'catalog.html' or args['thredds_link'] == 'enhancedCatalog.html':
#         thredds_catalog_url = thredds_catalog_url  + 'catalog/' + args['thredds_link']
#     elif args['thredds_link'].split('/')[-1] == 'catalog.html':
#         thredds_catalog_url = thredds_catalog_url  + args['thredds_link']
#     else:
#         thredds_catalog_url = thredds_catalog_url + args['thredds_link']
#     print("THREDDS URL: ", thredds_catalog_url)

    
#     if request.GET:
#         thredds_catalog_url = thredds_catalog_url + '?'
#         for key, value in request.GET.items():
#             print("GET parameter - key: ", key, "value: ", value)

#             print("Get request: ", args['thredds_link'])
            
                
#             thredds_catalog_url = thredds_catalog_url  + key +'='+ value

#     try:
#         print('REQUEST: ', request, '\nURL: ', thredds_catalog_url)
#         response = requests.get(thredds_catalog_url)
#         # print('response: \n', response.text)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         thredds_content = response.text
#         # print("thredds_content: ", thredds_content)

#         # Parse the HTML content
#         soup = BeautifulSoup(thredds_content, 'html.parser')
#         # Replace <img> tags with Bootstrap folder icons
#         i_tag = soup.new_tag('i', **{'class': 'bi bi-folder'})
#         a_tag = soup.new_tag('a', **{'href': 'catalog.html'})
#         for img in soup.find_all('img', alt='Folder'):
#             img.replace_with(i_tag)
#         try:
#             print("trying...")
#             buttons = soup.find_all('a', href='http://thredds/catalog/catalog.html')
#             for button in buttons:
#                 print("button: ", button)
#                 button['href'] = 'catalog/catalog.html'
#             print("replaced")
#         except:
#             print("except")
#             pass
#         # Find the div element with id "footer"
#         footer_div = soup.find('div', id='footer')
#         header_div = soup.find('div', id='header')
#         # Delete all parent divs of the footer_div
#         footer_div.decompose()
#         header_div.decompose()
#         div = soup.find('div', class_='container')
#         print('catalog\n\n', div)
#         return render(request, 'swn/thredds.html', {'thredds_content': str(div)})


#     except requests.RequestException as e:
#         # Handle request exception, e.g., log the error
#         thredds_content = f"Error: {e}"

#     # return render(request, 'swn/thredds.html', {'thredds_content': soup})

# dev feature displays all bootstrap colors etc.
def bootstrap(request):
    return render(request, 'swn/bootstrap_colors.html')

def load_polygon(request, entity, polygon_id):
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

# generate jsons of all choices in the field-menu page for faster update whithin UI
# def field_edit(request, id):
#     print("field_menu id: ", id)
    
#     start_time = time.time()

#     crop_form  = forms.CropForm()
#     crop_cultivar_form = monica_forms.CultivarParametersForm()
#     user_field = models.UserField.objects.get(id=id)
#     name = user_field.name
#     print("field_menu Checkpoint 1: ", (time.time() - start_time))
#     # retrieving soil data from db:
#     soil_profile_polygon_ids = user_field.soil_profile_polygon_ids['buek_polygon_ids']
    
#     land_usage_choices = {}

#     print("field_menu Checkpoint 2: ", (time.time() - start_time))
    
#     soil_data = models.BuekSoilProfileHorizon.objects.select_related('bueksoilprofile').filter(
#             bueksoilprofile__polygon_id__in=soil_profile_polygon_ids
#             ).order_by('bueksoilprofile__polygon_id', '-bueksoilprofile__area_percenteage', 'bueksoilprofile__id', 'horizont_nr')
#     unique_land_usages = soil_data.values_list(
#         'bueksoilprofile__landusage_corine_code', 'bueksoilprofile__landusage'
#         ).order_by(
#             'bueksoilprofile__landusage_corine_code', 'bueksoilprofile__landusage'
#             ).distinct(
#                 'bueksoilprofile__landusage_corine_code', 'bueksoilprofile__landusage'
#                 )
    
#     for code, usage in unique_land_usages:
#         if code != 51:
#             land_usage_choices[code] = usage
#     print('land_usage_choices', land_usage_choices)
#     # Assuming soil_data is the queryset obtained earlier
#     print("field_menu Checkpoint 2-1: ", (time.time() - start_time))
    
#     data_json = {}
#     # Now, you have sets containing distinct values for each field
#     for landusage_corine_code in list(land_usage_choices.keys()):
#         data_json[landusage_corine_code] = {}


#     for item in soil_data:
#         try:
#             if item.bueksoilprofile.landusage_corine_code != 51:
            
#                 if item.bueksoilprofile.system_unit not in data_json[item.bueksoilprofile.landusage_corine_code]:
#                     data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit] = {
#                         'area_percentages': {item.bueksoilprofile.area_percenteage},
#                         'soil_profiles': {item.bueksoilprofile.area_percenteage: {item.bueksoilprofile.id: {'horizons': {}}}}
#                     }
#                 else:
#                     data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['area_percentages'].add(item.bueksoilprofile.area_percenteage)
#                     if item.bueksoilprofile.area_percenteage not in data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles']:
#                         data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage] = {item.bueksoilprofile.id: {'horizons': {}}}

#                     if item.bueksoilprofile.id not in data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage]:
#                         data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage] = {item.bueksoilprofile.id: {'horizons': {}}}

                

#                 if item.bulk_density_class_id is not None:
#                     # print('horizon.bulk_density_class_id', horizon.bulk_density_class.bulk_density_class)
#                     bulk_density_class = item.bulk_density_class.bulk_density_class
#                     bulk_density = item.bulk_density_class.raw_density_g_per_cm3
#                 else:
#                     bulk_density_class = 'no data'
#                     bulk_density = 'no data'


#                 if item.humus_class_id is not None:
#                     humus_class = item.humus_class.humus_class
#                     humus_corg = item.humus_class.corg
#                 else:
#                     humus_class = 'no data'
#                     humus_corg = 'no data'
    
#                 if item.ka5_texture_class_id is not None:
#                     ka5_texture_class = item.ka5_texture_class.ka5_soiltype
#                     sand = item.ka5_texture_class.sand
#                     clay = item.ka5_texture_class.clay
#                     silt = item.ka5_texture_class.silt
#                 else:
#                     ka5_texture_class = 'no data'
#                     sand = 'no data'
#                     clay = 'no data'
#                     silt = 'no data'

#                 if item.ph_class_id is not None:
#                     ph_class = item.ph_class.ph_class
#                     ph_lower_value = item.ph_class.ph_lower_value
#                     ph_upper_value = item.ph_class.ph_upper_value
#                 else:
#                     ph_class = 'no data'
#                     ph_lower_value = 'no data'
#                     ph_upper_value = 'no data'

#                 data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles']\
#                     [item.bueksoilprofile.area_percenteage][item.bueksoilprofile.id]['horizons'][item.horizont_nr] = {
#                     'obergrenze_m': item.obergrenze_m,
#                     'untergrenze_m': item.untergrenze_m,
#                     'stratigraphie': item.stratigraphie,
#                     'herkunft': item.herkunft,
#                     'geogenese': item.geogenese,
#                     'fraktion': item.fraktion,
#                     'summe': item.summe,
#                     'gefuege': item.gefuege,
#                     'torfarten': item.torfarten,
#                     'substanzvolumen': item.substanzvolumen,
#                     'bulk_density_class': bulk_density_class,
#                     'bulk_density': bulk_density,
#                     'humus_class': humus_class,
#                     'humus_corg': humus_corg,
#                     'ka5_texture_class': ka5_texture_class,
#                     'sand': sand,
#                     'clay': clay,
#                     'silt': silt,
#                     'ph_class': ph_class,
#                     'ph_lower_value': ph_lower_value,
#                     'ph_upper_value': ph_upper_value,                    
#                 }
#         except:
#             print("except block XX")
           
#     for landusage_corine_code in data_json:
#         for system_unit in data_json[landusage_corine_code]:
#             data_json[landusage_corine_code][system_unit]['area_percentages']  = sorted(list(data_json[landusage_corine_code][system_unit]['area_percentages'] ))

    

#     soil_profile_form = forms.SoilProfileSelectionForm()
#     soil_profile_form.set_choices(land_usage_choices)

#     today = date.today()
#     start_date = today.replace(year=(today.year -1))
#     end_month = (today.month + 6) % 12
#     end_date = today.replace(month=end_month)
#     if today.month > 6:
#         end_date = end_date.replace(year=(today.year+1))
    

#     date_picker_str = {
#         'start_date': start_date.strftime('%d/%m/%Y'),
#         'end_date': end_date.strftime('%d/%m/%Y')
#     }
#     print("startEndDate: ", type(date_picker_str["start_date"]))

#     print("field_menu Checkpoint 5: ", (time.time() - start_time))
#     data_menu = {
#         'crop_form': crop_form,
#         'crop_cultivar_form': crop_cultivar_form,
#         'soil_profile_form': soil_profile_form,
#         'text': name,
#         'id': id,
#         'polygon_ids': soil_profile_polygon_ids,
#         'system_unit_json': json.dumps(data_json),
#         'landusage_choices': json.dumps(land_usage_choices),
#         'date_picker': date_picker_str
        
#     }
#     with open('land_usage_choices.json', 'w') as f:
#         json.dump(land_usage_choices, f)
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print('elapsed_time', elapsed_time, ' seconds')
#     return render(request, 'swn/field_projects_edit.html', data_menu)


def field_edit(request, id):
    print("field_menu id: ", id)
    
    start_time = time.time()

    crop_form = forms.CropForm()
    crop_cultivar_form = monica_forms.CultivarParametersForm()
    user_field = models.UserField.objects.get(id=id)
    name = user_field.name
    print("field_menu Checkpoint 1: ", (time.time() - start_time))
    
    soil_profile_polygon_ids = user_field.soil_profile_polygon_ids['buek_polygon_ids']
    
    print("field_menu Checkpoint 2: ", (time.time() - start_time))
    
    # Retrieve unique land usage choices
    unique_land_usages = models.BuekSoilProfile.objects.filter(
        polygon_id__in=soil_profile_polygon_ids
    ).values_list('landusage_corine_code', 'landusage').distinct()

    # Filter out certain codes, if needed
    land_usage_choices = {code: usage for code, usage in unique_land_usages if code != 51}
    print('land_usage_choices', land_usage_choices)

    print("field_menu Checkpoint 2-1: ", (time.time() - start_time))
    
    # Initialize data_json with land usage codes
    data_json = {code: {} for code in land_usage_choices.keys()}
    
    # Loop through soil data and populate data_json
    soil_data = models.BuekSoilProfileHorizon.objects.select_related('bueksoilprofile').filter(
        bueksoilprofile__polygon_id__in=soil_profile_polygon_ids
    ).order_by('bueksoilprofile__landusage_corine_code', 'bueksoilprofile__system_unit', 'bueksoilprofile__area_percenteage', 'horizont_nr')

    for item in soil_data:
        try:
            if item.bueksoilprofile.landusage_corine_code != 51:
                land_code = item.bueksoilprofile.landusage_corine_code
                system_unit = item.bueksoilprofile.system_unit
                area_percentage = item.bueksoilprofile.area_percenteage
                profile_id = item.bueksoilprofile.id
                horizon_nr = item.horizont_nr

                if system_unit not in data_json[land_code]:
                    data_json[land_code][system_unit] = {
                        'area_percentages': set(),
                        'soil_profiles': {}
                    }

                data_json[land_code][system_unit]['area_percentages'].add(area_percentage)

                if area_percentage not in data_json[land_code][system_unit]['soil_profiles']:
                    data_json[land_code][system_unit]['soil_profiles'][area_percentage] = {}

                if profile_id not in data_json[land_code][system_unit]['soil_profiles'][area_percentage]:
                    data_json[land_code][system_unit]['soil_profiles'][area_percentage][profile_id] = {'horizons': {}}

                # Populate horizon data
                data_json[land_code][system_unit]['soil_profiles'][area_percentage][profile_id]['horizons'][horizon_nr] = {
                    'obergrenze_m': item.obergrenze_m,
                    'untergrenze_m': item.untergrenze_m,
                    'stratigraphie': item.stratigraphie,
                    'herkunft': item.herkunft,
                    'geogenese': item.geogenese,
                    'fraktion': item.fraktion,
                    'summe': item.summe,
                    'gefuege': item.gefuege,
                    'torfarten': item.torfarten,
                    'substanzvolumen': item.substanzvolumen,
                    'bulk_density_class': item.bulk_density_class.bulk_density_class if item.bulk_density_class_id is not None else 'no data',
                    'bulk_density': item.bulk_density_class.raw_density_g_per_cm3 if item.bulk_density_class_id is not None else 'no data',
                    'humus_class': item.humus_class.humus_class if item.humus_class_id is not None else 'no data',
                    'humus_corg': item.humus_class.corg if item.humus_class_id is not None else 'no data',
                    'ka5_texture_class': item.ka5_texture_class.ka5_soiltype if item.ka5_texture_class_id is not None else 'no data',
                    'sand': item.ka5_texture_class.sand if item.ka5_texture_class_id is not None else 'no data',
                    'clay': item.ka5_texture_class.clay if item.ka5_texture_class_id is not None else 'no data',
                    'silt': item.ka5_texture_class.silt if item.ka5_texture_class_id is not None else 'no data',
                    'ph_class': item.ph_class.ph_class if item.ph_class_id is not None else 'no data',
                    'ph_lower_value': item.ph_class.ph_lower_value if item.ph_class_id is not None else 'no data',
                    'ph_upper_value': item.ph_class.ph_upper_value if item.ph_class_id is not None else 'no data',                    
                }
        except Exception as e:
            print("Exception occurred:", e)
           
    # Sort area percentages
    for land_code in data_json:
        for system_unit in data_json[land_code]:
            data_json[land_code][system_unit]['area_percentages'] = sorted(list(data_json[land_code][system_unit]['area_percentages']))

    # Initialize and format date picker strings
    today = date.today()
    start_date = today.replace(year=(today.year - 1))
    end_month = (today.month + 6) % 12
    end_date = today.replace(month=end_month)
    if today.month > 6:
        end_date = end_date.replace(year=(today.year + 1))

    date_picker_str = {
        'start_date': start_date.strftime('%d/%m/%Y'),
        'end_date': end_date.strftime('%d/%m/%Y')
    }

    print("startEndDate: ", type(date_picker_str["start_date"]))

    print("field_menu Checkpoint 5: ", (time.time() - start_time))

    data_menu = {
        'crop_form': crop_form,
        'crop_cultivar_form': crop_cultivar_form,
        'soil_profile_form': forms.SoilProfileSelectionForm().set_choices(land_usage_choices),
        'text': name,
        'id': id,
        'polygon_ids': soil_profile_polygon_ids,
        'system_unit_json': json.dumps(data_json),
        'landusage_choices': json.dumps(land_usage_choices),
        'date_picker': date_picker_str
    }

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('elapsed_time', elapsed_time, ' seconds')
    return render(request, 'swn/field_projects_edit.html', data_menu)


