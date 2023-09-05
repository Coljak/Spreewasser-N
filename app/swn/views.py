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
import requests
from .forms import PolygonSelectionForm
from . import forms
from . import models
from app.helpers import is_ajax
from bs4 import BeautifulSoup
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic

from .utils import get_geolocation
import random

from .data import calc_list, calc_dict


def get_csrf_token(request):
    data = {
        'csrfToken': csrf.get_token(request)
    }
    return JsonResponse(data)



class IndexView(TemplateView):
    template_name = "swn/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'BASIC INJECTION'
        return context


def impressum_information(request):
    return render(request, 'swn/impressum_information.html')

# this renders the example for the NetCDF timelapse from https://github.com/socib/Leaflet.TimeDimension
# an alternative could be https://github.com/smlum/netcdf-vis
def timelapse(request):
    return render(request, 'swn/map_thredds.html')

def timelapse_c(request):
    return render(request, 'swn/map_thredds_colja.html')

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

    # get all data from general calclations
    shp = models.GeoData.objects.all()

    # state, county and district choices

    state_county_district_form = PolygonSelectionForm(request.POST or None)

    if state_county_district_form.is_valid():
        selected_states = state_county_district_form.cleaned_data['states']
        selected_counties = state_county_district_form.cleaned_data['counties']
        selected_districts = state_county_district_form.cleaned_data['districts']
        
        # Process the selected polygons and pass the data to the map template


    data = {'shp': shp, 
            'user_projects': user_projects, 
            'user_field_form': field_name_form,
            'crop_form': crop_form, 
            'project_form': project_form,
            'state_county_district_form': state_county_district_form,
            }
    


    return render(request, 'swn/user_dashboard.html', data)


@login_required
def userinfo(request):
    return render(request, 'swn/userinfo.html')


class ChartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'swn/chart.html', {})


def get_chart(request, field_id, crop_id):
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

    return JsonResponse({'user_fields': list(user_fields.values('id', 'user', 'name', 'geom_json')), 'user_projects': list(user_projects.values())})

async def get_user_fields_async(request):
    task1 = asyncio.create_task(models.UserProject.objects.filter(field__user=request.user))
    task2 = asyncio.create_task(models.UserField.objects.filter(user=request.user))
    await asyncio.wait([task1, task2])
    return JsonResponse({'user_fields': list(task1.values('id', 'user', 'name', 'geom_json')), 'user_projects': list(task2.values())})

# userfields are updated for the leaflet sidebar
@login_required
# @action_permission
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
    return redirect('swn:user_dashboard')


# This view eliminates the AJAX request above
@login_required
@csrf_protect
async def save_user_field_async(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        
        name = body['name']
        geom = json.loads(body['geom'])
        geos = GEOSGeometry(body['geom'], srid=4326)
        user = request.user
        instance = models.UserField()
        instance.name = name
        instance.geom_json = geom
        instance.geom = geos
        instance.user = user
        instance.save()
        
        models.UserField.get_intersecting_soil_data(id)
        
        return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
    else: 
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
            geom = json.loads(body['geom'])
            geos = GEOSGeometry(body['geom'], srid=4326)
            user = request.user
            instance = models.UserField(name=name, geom_json=geom, geom=geos, user=user)
            instance.save()

            instance.get_intersecting_soil_data()
            return JsonResponse({'name': instance.name, 'geom_json': instance.geom_json, 'id': instance.id})
        
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



def thredds_wms_view(request):
    thredds_server_url = 'https://thredds.socib.es/thredds/wms'  # Replace with the actual Thredds server URL

    # Proxy the request to the Thredds server
    headers = {'User-Agent': request.META.get('HTTP_USER_AGENT')}
    response = request.get(thredds_server_url, headers=headers, params=request.GET)
    
    # Return the Thredds server response as the response of your Django view
    content_type = response.headers.get('Content-Type', 'application/octet-stream')
    return HttpResponse(response.content, content_type=content_type)


def bootstrap(request):
    return render(request, 'swn/bootstrap_colors.html')

def multiselect(request):
    return render(request, 'swn/multiselect.html')


    
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
    

def field_menu(request, id):
    crop_form  = forms.CropForm(request.POST or None)
    name = models.UserField.objects.get(id=id).name
    data_menu = {
        'crop_form': crop_form,
        'text': name,
        'id': id,
    }
    return render(request, 'swn/field_projects_edit.html', data_menu)

def buek_test_view(request, buek_id):
    buek_data_url = "https://fisbo.bgr.de/app/FISBoBGR_Profilanzeige/getProfile.php?"
    params = {
        'KARTE': 'BUEK200',
        'LEGNR': buek_id,
    }
    response = requests.get(buek_data_url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    profiles = soup.find_all('table', class_='profil')
    data = {}
    for profile in profiles:
        table_rows = profile.find_all('tr')
        print(table_rows)
        land_cover_code = profile.find('title', class_='Landnutzung nach Corine 2000')
        profile_img = profile.find('table', class_='showProfile')
        profile_img_html = profile_img.prettify()

    # print(response.content)
    return HttpResponse(response.content, content_type="text/html")

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


    # params = {
    #     'service': 'WMS',
    #     'version': '1.1.1',
    #     'request': 'GetFeatureInfo',
    #     'layers': 3,
    #     'styles': '',
    #     'format': 'text/xml',
    #     'transparent': 'true',
    #     'srs': 'EPSG:4326',
    #     
    #     'bbox': bbox,
    #     'width': 200,
    #     'height': 200,
    # }

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
    # if response.status_code == 200:
    #     import os
    #     from pathlib import Path
        
    #     image_filename = f'map_image_{id}.png'
    #     image_filepath = os.path.join('/app/swn/templates/swn/wms_testfolder', image_filename)
    #     print('IMAGE FILEPATH', image_filepath)

    #     with open(image_filepath, 'wb') as f:
    #         f.write(response.content)

    # content = response.content
    # for key in response.__dict__.keys():
    #     print("content\n", key, response.__dict__[key])
    # with open('map_image.png', 'wb') as f:
    #     f.write(image_content)

def get_soil_data(request, id):
    print("VIEW get_soil_data EXECUTED")
    user_field = models.UserField.objects.get(id=id)
    print("user_field.soil_profile_polygon_ids", user_field.soil_profile_polygon_ids)
    #soil_profiles = models.SoilProfile.objects.filter(polygon_id__in=user_field.soil_profile_polygon_ids)
    intersecting_buek_data = models.BuekData.objects.filter(polygon_id_in_buek__in=user_field.soil_profile_polygon_ids['buek_polygon_ids'])
    
    print('intersecting_buek_data', intersecting_buek_data)

    data = {}
    for polygon_id in user_field.soil_profile_polygon_ids['buek_polygon_ids']:
        print(polygon_id)
        
        
        for obj in intersecting_buek_data:
            polygon_id_in_buek = obj.polygon_id_in_buek
            profile_id_in_polygon = obj.profile_id_in_polygon
            horizon_id = obj.horizon_id

            data.setdefault(polygon_id_in_buek, {})
            data[polygon_id_in_buek].setdefault(profile_id_in_polygon, {})
            data[polygon_id_in_buek][profile_id_in_polygon].setdefault(horizon_id, {})

            # this only contains parameters that are not null
            data[polygon_id_in_buek][profile_id_in_polygon][horizon_id] = {
                
                'avg_range_percentage_of_area': obj.avg_range_percentage_of_area,
                'layer_depth': obj.layer_depth,
                'bulk_density': obj.bulk_density,
                'raw_density': obj.raw_density,
                'soil_organic_carbon': obj.soil_organic_carbon,
                'ph': obj.ph,
                'ka5_texture_class': obj.ka5_texture_class,
                'sand': obj.sand,
                'clay': obj.clay,
                'silt': obj.silt,
                'layer_description': obj.layer_description,
                'is_in_groundwater': obj.is_in_groundwater,
                'is_impenetrable': obj.is_impenetrable,
                
                # Add other parameters here...
                }
    

    print("data", data)
    #return JsonResponse(user_field.soil_profile_polygon_ids)
    return JsonResponse(data)
 