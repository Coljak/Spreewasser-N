import json, asyncio
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
import requests
from . import forms
from . import models

from toolbox import models as toolbox_models
from app.helpers import is_ajax
import xmltodict
from datetime import datetime

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
    url = 'http://thredds:8080/thredds/catalog/testAll/data/DWD_SpreeWasser_N_cf_v4/catalog.xml'

    response = requests.get(url)
    catalog_dict = xmltodict.parse(response.content)

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

    catalog = {'catalog': catalog_dict_list}
    catalog_json = json.dumps(catalog_dict_list, indent=2)

    return render(request, 'swn/thredds_catalog.html', {'catalog_json': catalog_dict_list})


def timelapse_test_django_passthrough(request):
    return render(request, 'swn/map_thredds_4.html')

def timelapse_test_django_passthrough_wms(request, netcdf):
    # example netcdf from frontend: zalf_pr_amber_2009_v1-0_cf_v4.nc 

    print("timelapse_test_django_passthrough_wms", netcdf)
    url = 'http://thredds:8080/thredds/wms/testAll/data/DWD_SpreeWasser_N_cf_v4/' + netcdf
    params = request.GET.dict()
    print("params", params)
    print("url", url)
    # Timeseries legend image
    layer_name = 'pr'
    legendUrl = '{wmsUrl}?REQUEST=GetLegendGraphic&PALETTE=default&LAYERS={layer_name}'.format(wmsUrl=url, layer_name=layer_name)

    # Timeseries WMS
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Return the response content to the frontend
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        # Handle request exception, e.g., log the error
        return HttpResponse(f"Error: {e}", content_type='text/plain')


def timelapse_test(request):
    url = 'https://thredds.socib.es/thredds/wms/operational_models/oceanographical/wave/model_run_aggregation/sapo_ib/sapo_ib_best.ncd'
    url2 = 'http://0.0.0.0:8080/thredds/wms/testAll/data/zalf_hurs_amber_2007_v1-0_ck_v14_compressed_9.nc?service=WMS&version=1.3.0&request=GetMap&layers=relative_humidity&styles=&format=image%2Fpng&transparent=true&height=256&width=256&crs=EPSG%3A4326&bbox=5.564783468,47.136744752,15.57241882,55.058996788&time=2007-01-01T00%3A00%3A00.000Z'
    url_3 = 'http://thredds:8080/thredds/wms/testAll/data/zalf_hurs_amber_2007_v1-0_ck_v14_compressed_9.nc'
    wms_params = {
        'servive': 'WMS',
        'version': '1.3.0',        
        'request': 'GetCapabilities',
        'layers': 'significant_wave_height',
        'format': 'image/png',
        'transparent': 'true',
        # 'colorscalerange': '0,3',
        # 'bbox': '156543.03392804097,4852834.051769271,313086.06785608194,5009377.085697314',

    }
    
    # response = requests.get(url, params=wms_params)
    response = requests.get(url_3)
    print("response\n", response)
    return HttpResponse(response.content, content_type='image/png')

def timelapse_test_2(request):
    return render(request, 'swn/map_thredds_2.html')

def sign_up(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        print("Sign_up form", form)
        if form.is_valid():
            print("Sign_up is_valid")
            user = form.save()
            print("Sign_up user saved", user)
            login(request, user)
            return redirect('swn:user_dashboard')
    else:
        form = forms.RegistrationForm()
        print("Sign_up else")

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
        print("Register ELSE")
        user_form = forms.UserForm()

    return render(request, 'swn/registration.html',
                  {'user_form': user_form,
                   # 'pk': user.id,
                   'registered': registered})

def user_login(request):
    print("USER_LOGIN")
    if request.method == "POST":
        print("POST:", request.POST.values())
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, name=username, password=password)
        # if '@' in username:
        #     email = username
        #     user = authenticate(email=email, password=password)
        # else:
        #     user = authenticate(name=username, password=password)

        print("email:", email, "password: ", password, "username: ", username)
        #user = authenticate(email=email, password=password)
        if user:
            print("IF USER")
            if user.is_active:

                login(request, user)
                initial = user.username
                return HttpResponseRedirect(reverse('swn:user_dashboard'))

            else:
                return HttpResponse("Account is not active!")
            
        # TODO make this go to handle alerts
        else:
            print("ELSE USER")
            return JsonResponse({'alert': "the login failed"})

    else:
        login_form = forms.LoginForm()
        print("login_form: ", login_form)
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
                'irrigation_otput': user_field.irrigation_output,

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

# @login_required
# def userinfo(request):
#     return render(request, 'swn/userinfo.html')


# class ChartView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'swn/chart.html', {})


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
        # rand = random.randint(0, len(key_list) - 1)
        # key = key_list[rand]
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

# async def get_user_fields_async(request):
#     task1 = asyncio.create_task(models.UserProject.objects.filter(field__user=request.user))
#     task2 = asyncio.create_task(models.UserField.objects.filter(user=request.user))
#     await asyncio.wait([task1, task2])
#     return JsonResponse({'user_fields': list(task1.values('id', 'user', 'name', 'geom_json')), 'user_projects': list(task2.values())})

# userfields are updated for the leaflet sidebar
@login_required
# @action_permission
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
            print("UserField Save: ", name, geom, user)
            instance.save()
            print("UserfIeld saved")
            instance.get_intersecting_soil_data()
            print("get inetrsecting soil data")
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

def thredds_wms_view(request, **args):
    print("\nNew call of thredds_wms_view \n")
    thredds_catalog_url = 'http://thredds:8080/thredds/'
    print("args: ", args)

    if args == {}:
            thredds_catalog_url = thredds_catalog_url + 'catalog/catalog.html'
    elif args['thredds_link'].split('/')[-1].split('.')[-1] not in ('html', 'nc', 'ncd', 'ncml', 'xml'):
        return HttpResponse()
    elif args['thredds_link'] == 'catalog.html' or args['thredds_link'] == 'enhancedCatalog.html':
        thredds_catalog_url = thredds_catalog_url  + 'catalog/' + args['thredds_link']
    elif args['thredds_link'].split('/')[-1] == 'catalog.html':
        thredds_catalog_url = thredds_catalog_url  + args['thredds_link']
    else:
        thredds_catalog_url = thredds_catalog_url + args['thredds_link']
    print("THREDDS URL: ", thredds_catalog_url)

    
    if request.GET:
        thredds_catalog_url = thredds_catalog_url + '?'
        for key, value in request.GET.items():
            print("GET parameter - key: ", key, "value: ", value)

            print("Get request: ", args['thredds_link'])
            
                
            thredds_catalog_url = thredds_catalog_url  + key +'='+ value

    try:
        print('REQUEST: ', request, '\nURL: ', thredds_catalog_url)
        response = requests.get(thredds_catalog_url)
        # print('response: \n', response.text)
        response.raise_for_status()  # Raise an exception for HTTP errors
        thredds_content = response.text
        # print("thredds_content: ", thredds_content)

        # Parse the HTML content
        soup = BeautifulSoup(thredds_content, 'html.parser')
        # Replace <img> tags with Bootstrap folder icons
        i_tag = soup.new_tag('i', **{'class': 'bi bi-folder'})
        a_tag = soup.new_tag('a', **{'href': 'catalog.html'})
        for img in soup.find_all('img', alt='Folder'):
            img.replace_with(i_tag)
        try:
            print("trying...")
            buttons = soup.find_all('a', href='http://thredds/catalog/catalog.html')
            for button in buttons:
                print("button: ", button)
                button['href'] = 'catalog/catalog.html'
            print("replaced")
        except:
            print("except")
            pass
        # Find the div element with id "footer"
        footer_div = soup.find('div', id='footer')
        header_div = soup.find('div', id='header')
        # Delete all parent divs of the footer_div
        footer_div.decompose()
        header_div.decompose()
        div = soup.find('div', class_='container')
        print('catalog\n\n', div)
        return render(request, 'swn/thredds.html', {'thredds_content': str(div)})

        # Get the first div element with the class "content"
        div = ''
        try:
            div = soup.find('div', class_='container')
            catalog_contents = div.find_all('div', class_='content')
            catalog = ""
            if len(catalog_contents) > 1:
                catalog = catalog_contents[1]
            else:
                catalog = catalog_contents[0]
        except:
            div = soup.find('table')

        return render(request, 'swn/thredds.html', {'thredds_content': str(div)})
    except requests.RequestException as e:
        # Handle request exception, e.g., log the error
        thredds_content = f"Error: {e}"

    # return render(request, 'swn/thredds.html', {'thredds_content': soup})




def thredds_wms_view_2(request):
    # # thredds_server_url = settings.THREDDS_URL
    # # thredds_server_url = 'http://thredds:8080/thredds/wms/allDataScan/zalf_hurs_amber_2007_v1-0.nc'  # Replace with the actual Thredds server URL
    # thredds_url = 'http://thredds:8080/thredds/catalog/catalog.html'
    # # Proxy the request to the Thredds server
    # headers = {'User-Agent': request.META.get('HTTP_USER_AGENT')}
    # # response = request.get(thredds_server_url, headers=headers, params=request.GET)
    # # response = request.get(thredds_server_url,  params=request.GET)
    # response = request.get(thredds_url)
    
    # # Return the Thredds server response as the response of your Django view
    # content_type = response.headers.get('Content-Type', 'application/octet-stream')
    # #content_type2 = response.headers['Content-Type']
    # return HttpResponse(response.content, content_type=content_type)
    # Replace 'http://127.0.0.1:8088/thredds/catalog/catalog.html' with your Thredds catalog URL
    thredds_catalog_url = 'http://127.0.0.1:8088/thredds/catalog/catalog.html'
    
    # Redirect the user to the Thredds catalog URL
    return redirect(thredds_catalog_url)


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
def field_menu(request, id):
    print("field_menu id: ", id)
    
    start_time = time.time()

    crop_form  = forms.CropForm(request.POST or None)
    name = models.UserField.objects.get(id=id).name
    user_field = models.UserField.objects.get(id=id)
    print("field_menu Checkpoint 1: ", (time.time() - start_time))
    soil_profile_polygon_ids = user_field.soil_profile_polygon_ids['buek_polygon_ids']


    unique_land_usages = models.BuekSoilProfile.objects.filter(
        polygon_id__in=soil_profile_polygon_ids
    ).values_list('landusage_corine_code', 'landusage').distinct()
    land_usage_choices = {}
    for code, usage in unique_land_usages:
        if code != 51:
            land_usage_choices[code] = usage
    print('land_usage_choices', land_usage_choices)

    print("field_menu Checkpoint 2: ", (time.time() - start_time))
    
    soil_data = models.BuekSoilProfileHorizon.objects.select_related('bueksoilprofile').filter(
            bueksoilprofile__polygon_id__in=soil_profile_polygon_ids
            ).order_by('bueksoilprofile__polygon_id', '-bueksoilprofile__area_percenteage', 'bueksoilprofile__id', 'horizont_nr')
    
    # Assuming soil_data is the queryset obtained earlier
    print("field_menu Checkpoint 2-1: ", (time.time() - start_time))
    # Extracting distinct values for the specified fields
    distinct_landusage_ids = set(item.bueksoilprofile.landusage_corine_code for item in soil_data)
    print("field_menu Checkpoint 2-2: ", (time.time() - start_time))
    data_json = {}
    # Now, you have sets containing distinct values for each field
    for landusage_corine_code in distinct_landusage_ids:
        data_json[landusage_corine_code] = {}


    for item in soil_data:
        try:
            if item.bueksoilprofile.landusage_corine_code != 51:
            
                if item.bueksoilprofile.system_unit not in data_json[item.bueksoilprofile.landusage_corine_code]:
                    data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit] = {
                        'area_percentages': {item.bueksoilprofile.area_percenteage},
                        'soil_profiles': {item.bueksoilprofile.area_percenteage: {item.bueksoilprofile.id: {'horizons': {}}}}
                    }
                else:
                    data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['area_percentages'].add(item.bueksoilprofile.area_percenteage)
                    if item.bueksoilprofile.area_percenteage not in data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles']:
                        data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage] = {item.bueksoilprofile.id: {'horizons': {}}}

                    if item.bueksoilprofile.id not in data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage]:
                        data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles'][item.bueksoilprofile.area_percenteage] = {item.bueksoilprofile.id: {'horizons': {}}}

                

                if item.bulk_density_class_id is not None:
                    # print('horizon.bulk_density_class_id', horizon.bulk_density_class.bulk_density_class)
                    bulk_density_class = item.bulk_density_class.bulk_density_class
                    bulk_density = item.bulk_density_class.raw_density_g_per_cm3
                else:
                    bulk_density_class = 'no data'
                    bulk_density = 'no data'


                if item.humus_class_id is not None:
                    humus_class = item.humus_class.humus_class
                    humus_corg = item.humus_class.corg
                else:
                    humus_class = 'no data'
                    humus_corg = 'no data'
    
                if item.ka5_texture_class_id is not None:
                    ka5_texture_class = item.ka5_texture_class.ka5_soiltype
                    sand = item.ka5_texture_class.sand
                    clay = item.ka5_texture_class.clay
                    silt = item.ka5_texture_class.silt
                else:
                    ka5_texture_class = 'no data'
                    sand = 'no data'
                    clay = 'no data'
                    silt = 'no data'

                if item.ph_class_id is not None:
                    ph_class = item.ph_class.ph_class
                    ph_lower_value = item.ph_class.ph_lower_value
                    ph_upper_value = item.ph_class.ph_upper_value
                else:
                    ph_class = 'no data'
                    ph_lower_value = 'no data'
                    ph_upper_value = 'no data'

                data_json[item.bueksoilprofile.landusage_corine_code][item.bueksoilprofile.system_unit]['soil_profiles']\
                    [item.bueksoilprofile.area_percenteage][item.bueksoilprofile.id]['horizons'][item.horizont_nr] = {
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
                    'bulk_density_class': bulk_density_class,
                    'bulk_density': bulk_density,
                    'humus_class': humus_class,
                    'humus_corg': humus_corg,
                    'ka5_texture_class': ka5_texture_class,
                    'sand': sand,
                    'clay': clay,
                    'silt': silt,
                    'ph_class': ph_class,
                    'ph_lower_value': ph_lower_value,
                    'ph_upper_value': ph_upper_value,                    
                }
        except:
            print("except block XX")
           
    for landusage_corine_code in data_json:
        for system_unit in data_json[landusage_corine_code]:
            data_json[landusage_corine_code][system_unit]['area_percentages']  = sorted(list(data_json[landusage_corine_code][system_unit]['area_percentages'] ))

    

    soil_profile_form = forms.SoilProfileSelectionForm()
    soil_profile_form.set_choices(land_usage_choices)

    today = date.today()
    start_date = today.replace(year=(today.year -1))
    end_month = (today.month + 6) % 12
    end_date = today.replace(month=end_month)
    if today.month > 6:
        end_date = end_date.replace(year=(today.year+1))
    

    date_picker = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }

    print("field_menu Checkpoint 5: ", (time.time() - start_time))
    data_menu = {
        'crop_form': crop_form,
        'soil_profile_form': soil_profile_form,
        'text': name,
        'id': id,
        'polygon_ids': soil_profile_polygon_ids,
        'system_unit_json': json.dumps(data_json),
        'landusage_choices': json.dumps(land_usage_choices),
        'date_picker': date_picker
        
    }
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('elapsed_time', elapsed_time, ' seconds')
    return render(request, 'swn/field_projects_edit.html', data_menu)



# def update_soil_profile_choices(request):
#     land_usage = request.GET.get('land_usage')
#     polygon_ids_str = request.GET.get('polygon_ids')
#     polygon_ids = [int(id_str) for id_str in polygon_ids_str.split(',')]

#     # Query BuekSoilProfile to get soil_profile choices based on the selected land_usage
#     soil_profile_choices = models.BuekSoilProfile.objects.filter(
#         landusage_corine_code=land_usage, polygon_id__in=polygon_ids
#     ).values_list('system_unit').distinct()

#     print('soil_profile_choices', soil_profile_choices)
#     choices_system_unit = [system_unit for system_unit in soil_profile_choices]
#     choices_area_percentage = [area_percenteage for area_percenteage in soil_profile_choices]

#     choices = {
#         'system_unit': choices_system_unit,
#         'area_percentage': choices_area_percentage,
#     }
    
#     print('system_unit choices', choices)

#     return JsonResponse(choices, safe=False)



def get_soil_data_from_wms(id):
    """"
    https://www.bgr.bund.de/DE/Themen/Boden/Informationsgrundlagen/Bodenkundliche_Karten_Datenbanken/BUEK200/Sachdatenbank/felder_und_parameter.html?nn=2960024
    """
    user_field = models.UserField.objects.get(id=id)
    user_field_geom = user_field.geom
    polygon = user_field_geom.geojson
    # bbox = ','.join(map(str, user_field_geom.extent))
    bbox = (47.5, 8.7, 47.6, 8.8)
    # print("bbox", bbox)

    wms_url = 'https://services.bgr.de/wms/boden/buek200/?'
    params = {
        'service': 'WMS',
        'version': '1.3.0',
        'request': 'GetCapabilities',
        
    }
    params2 = {
        'bbox':'-2210783.259641736%2C6171667.260493002%2C4510783.259641736%2C7228332.739506998',
        'bboxSR':'3857',
        'imageSR':'3857',
        'size':'1717%2C270',
        'dpi':'120',
        'format':'png32',
        'transparent':True,
        'layers':'show%3A0%2C1',
        'f':'image'
        }
    params2 = {
        'bbox':'-2210783.259641736%2C6171667.260493002%2C4510783.259641736%2C7228332.739506998',
        'bboxSR':'3857',
        'imageSR':'3857',
        'size':'1717%2C270',
        'dpi':'120',
        'format':'png32',
        'transparent':True,
        'layers':'show%3A0%2C1',
        'f':'image'
        }


    wml_url = 'https://services.bgr.de/wms/boden/buek200/?'
    """
    This is a set of working parameters for the buek REST-Api. 
    The request takes very long because the buek is split up in layers that define areas.
    56 Layers are being queried, only three seem to render a result. The result containing data
    refers to this 
    URL: https://fisbo.bgr.de/app/FISBoBGR_Profilanzeige/getProfile.php?KARTE=BUEK200&amp;LEGNR=311865"""
    params = {
        'SERVICE': 'WMS',
        'VERSION': '1.3.0',
        'REQUEST': 'GetFeatureInfo',
        'BBOX': '1198111.96795441047288477,6647127.53802930749952793,1351146.27870820206589997,6819672.87509871460497379',
        'CRS': 'EPSG:3857',
        'WIDTH': 902,
        'HEIGHT': 1017,
        'LAYERS': 50,
        'STYLES': '',
        'FORMAT': 'image/jpeg',
        'QUERY_LAYERS': 50,
        'INFO_FORMAT': 'text/html',
        'I': 469, 
        'J': 326,
        'FEATURE_COUNT': 10}

    response = requests.get(wms_url, params=params)
    print(response.headers)
  

