import json
from multiprocessing import managers
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from importlib.util import spec_from_file_location

from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login, logout
from django.contrib.gis.gdal import DataSource
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from . import forms
from . import models
from app.helpers import is_ajax

from .utils import get_geolocation


class IndexView(TemplateView):
    template_name = "swn/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'BASIC INJECTION'
        return context

class TestHTML(TemplateView):
    template_name = "swn/testhtml.html"


class CropListView(ListView):
    model = models.Crop


def home(request):
    return render(request, 'swn/home.html')

def impressum_information(request):
    return render(request, 'swn/impressum_information.html')


def form_sidebar(request):
    form = forms.FormSidebar()

    if request.method == 'POST':
        form = forms.FormSidebar(request.POST)

        if form.is_valid():
            print('data has come in...')
            print(form.cleaned_data['name'])
            print(form.cleaned_data['email'])
            print(form.cleaned_data['text'])
    return render(request, 'app/form_sidebar.html', {'form': form})


def register(request):

    registered = False

    if request.method == "POST":
        user_form = forms.UserForm(data=request.POST)
        # profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid(): # and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            # profile = profile_form.save(commit=False)
            # profile.user = user

            # profile.save()

            registered = True
        else:
            #print(user_form.errors, profile_form.errors)
            print(user_form.errors)

    else:
        user_form = forms.UserForm()
        #profile_form = UserProfileInfoForm()

    return render(request, 'user/registration.html',
                  {'user_form': user_form,
                   #'profile_form': profile_form,
                   'registered': registered})


@login_required
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:

                login(request, user)
                return HttpResponseRedirect(reverse('swn-index'))

            else:
                return HttpResponse("Account is not active!")

        else:
            return HttpResponse("the login failed")

    else:
        return render(request, 'registration/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('swn:swn_index'))


@login_required
def user_dashboard(request):
    user_fields = models.UserProject.objects.filter(field__user = request.user)
    #projects_json = serialize('json', projects)
    context = []
    for user_field in user_fields:
        if request.user == user_field.field.user:
            item = {
                'name': user_field.name,
                'user_name': user_field.field.user.name,
                'field': user_field.field.name,
                'irrigation_input': user_field.irrigation_input,
                'irrigation_otput': user_field.irrigation_output,
                'geom': user_field.field.geom,
                'field_id': user_field.field.id,
                'monica_calculation': user_field.calculation,
            }
            context.append(item)
            
    data = {'context': context}

    if is_ajax(request):
        geom = request.geom
    
    return render(request, 'swn/user_dashboard.html', data)

class UserCropSelection(CreateView):
    model = models.Crop
    template_name = 'app/user_dashboard.html'
    form_class = forms.FormCrops


def map(request):
    # ip = '80.187.68.143'
    # lat, lon = get_geolocation(ip)
    # print('LAT and LON detected: ', lat, lon)
    pilotregion = models.ProjectRegion.objects.get(id=1)
    print(pilotregion)
    context = {
        'pilotregion': pilotregion
    }

    return render(request, 'swn/map.html', context)


""" def map_overlay(request):
    template_name = 'rsmgui_nav.html'

    if request.POST.get("area-overlay"):
        polydata = serialize('geojson', ModelArea.objects.filter(name=request.POST.get("aoi-choice")))
        return HttpResponse(polydata, content_type='json')
 """

@login_required
def userinfo(request):
    return render(request, 'swn/userinfo.html')

def save_shape(request):
    if(request.method == 'POST'):
        name = request.POST.get('name')
        geom = request.POST.get('geom')
        user = request.POST.get('user')

        user_field = models.UserField(name=name, geom=geom, user=user)

class ChartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'swn/chart.html', {})

def get_chart(request, *args, **kwargs):
    from .data import monica_calc
    
    return  JsonResponse(monica_calc)

def save_user_field(request):
    if is_ajax(request):
        print("Save user field is AJAX")
        print(request)
    return JsonResponse({})

# from ajax: post_detail
@login_required
def calc_data(request, pk):
    obj = models.Post.objects.get(pk=pk)
    form = forms.PostForm()

    context = {
        'obj': obj,
        'form': form,
    }

    return render(request, 'posts/detail.html', context)

def get_user_fields(request):
    if is_ajax(request):
        user_projects = models.UserProject.objects.filter(field__user = request.user)
        user_fields = models.UserField.objects.filter(user = request.user)
        some_dict = serialize('json', user_fields)
        # for user_field in list(user_fields.values()):
        #     #some_dict[user_field.id] = user_field
        print("user_field", some_dict) 
        print("Request.user", request.user.id)

        return JsonResponse({'user_fields': list(user_fields.values()), 'user_projects': list(user_projects.values())})

@login_required
# @action_permission
def update_user_field(request, pk):
    obj = models.UserField.objects.get(pk=pk)
    if is_ajax(request):
        
        obj.name = request.POST.get('fieldName')
        obj.geom_json = request.POST.get('geomJson')
        obj.geom = request.POST.get('geomJson')
        
        obj.save()
        return JsonResponse({
            'fieldName': obj.name,
            'geom': obj.geom,
        })
    return redirect('swn:user_dashboard')
    

@login_required
@csrf_protect
# @action_permission
def save_user_field(request):
    
    form = forms.UserFieldForm(request.POST or None)
    if is_ajax(request):
        instance = form.save(commit=False)
        instance.name = request.POST.get('fieldName')
        instance.geom_json = request.POST.get('geomJson')
        instance.geom = request.POST.get('geomJson')
        instance.id = request.user.id
        instance.save()
        return JsonResponse({
            'fieldName': instance.name,
            'geom': instance.geom,
        })
    return redirect('swn:user_dashboard')





