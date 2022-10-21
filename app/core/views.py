from django.shortcuts import render

from importlib.util import spec_from_file_location
from multiprocessing import managers
from django.http import HttpResponse
from core.forms import UserForm
from django.shortcuts import render
#from requests import request
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, TemplateView, ListView, DetailView
from . import forms
from . import models

from .utils import get_geolocation


# Create your views here.
# def index(request):
#     return render(request, 'app/index.html')

class IndexView(TemplateView):
    template_name = "app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'BASIC INJECTION'
        return context


# class CropListView(DetailView):
#     context_object_name = 'crops'

#     model = models.Crop


# class CropDetailView(ListView):
#     context_object_name = 'crop_deatil'
#     model = models.Crop
#     template_name = 'app/crop_detail.html'


def home(request):
    return render(request, 'app/home.html')


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
        user_form = UserForm(data=request.POST)
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
        user_form = UserForm()
        #profile_form = UserProfileInfoForm()

    return render(request, 'registration/registration.html',
                  {'user_form': user_form,
                   #'profile_form': profile_form,
                   'registered': registered})


@login_required
def user_login(request):
    print("user_login KONTROLLPUNKT 1")
    if request.method == "POST":
        print("user_login KONTROLLPUNKT 2")
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("user_login KONTROLLPUNKT 3")

        user = authenticate(username=username, password=password)
        print("user_login KONTROLLPUNKT 4")
        if user:
            print("user_login KONTROLLPUNKT 5")
            if user.is_active:

                login(request, user)
                print("user_login KONTROLLPUNKT 7")
                return HttpResponseRedirect(reverse('index'))

            else:
                print("user_login KONTROLLPUNKT 8")
                return HttpResponse("Account is not active!")

        else:
            print("user_login KONTROLLPUNKT 9")
            print('...the login failed...')

            return HttpResponse("the login failed")

    else:
        print("user_login KONTROLLPUNKT 10")
        return render(request, 'registration/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def user_dashboard(request):
    return render(request, 'app/user_dashboard.html')


def map(request):
    # ip = '80.187.68.143'
    # lat, lon = get_geolocation(ip)
    # print('LAT and LON detected: ', lat, lon)

    return render(request, 'app/map.html')


""" def map_overlay(request):
    template_name = 'rsmgui_nav.html'

    if request.POST.get("area-overlay"):
        polydata = serialize('geojson', ModelArea.objects.filter(name=request.POST.get("aoi-choice")))
        return HttpResponse(polydata, content_type='json')
 """

# @login_required


def userinfo(request):
    return render(request, 'app/userinfo.html')
