from django.shortcuts import render

from importlib.util import spec_from_file_location
from pathlib import Path
from multiprocessing import managers
from django.http import HttpResponse
#from core.forms import FormCrops, UserForm
from django.shortcuts import render
#from requests import request
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, JsonResponse
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login, logout
from django.contrib.gis.gdal import DataSource
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
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
    projects = models.UserProject.objects.filter(field__user = request.user)
    #projects_json = serialize('json', projects)
    context = []
    for proj in projects:
        if request.user == proj.field.user:
            item = {
                'name': proj.name 
            }
            context.append(item)
    data = {'context': context}
    
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
