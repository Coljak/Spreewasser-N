import json

from multiprocessing import managers
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from importlib.util import spec_from_file_location
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView
from django.views.decorators.csrf import csrf_protect
from . import forms
from . import models
from app.helpers import is_ajax
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic

from .utils import get_geolocation
import random


class IndexView(TemplateView):
    template_name = "swn/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['injectme'] = 'BASIC INJECTION'
        return context


def impressum_information(request):
    return render(request, 'swn/impressum_information.html')

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
    user_fields = models.UserProject.objects.filter(field__user=request.user)
    # name_form = forms.UserFieldForm(request.POST or None)
    # projects_json = serialize('json', projects)
    crop_form = forms.CropForm(request.POST or None)
    project_form = forms.UserProjectForm()
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

    data = {'user_projects': user_projects, 'crop_form': crop_form, 'project_form': project_form}

    return render(request, 'swn/user_dashboard.html', data)


@login_required
def userinfo(request):
    return render(request, 'swn/userinfo.html')


class ChartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'swn/chart.html', {})


def get_chart(request, *args, **kwargs):
    from .data import monica_calc, monica_calc_1, monica_calc_2, monica_calc_3
    calc_list = [monica_calc, monica_calc_1, monica_calc_2, monica_calc_3]
    rand = random.randint(0, len(calc_list))

    return JsonResponse(calc_list[rand])


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
        user_projects = models.UserProject.objects.filter(
            field__user=request.user)
        user_fields = models.UserField.objects.filter(user=request.user)

    return JsonResponse({'user_fields': list(user_fields.values('id', 'user', 'name', 'geom_json')), 'user_projects': list(user_projects.values())})


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


@login_required
@csrf_protect
# @action_permission
def save_user_field(request):
    # if request.user.is_authenticated:
    # user = models.User.objects.get(user=request.user)
    print("request in views:", request.user)
    if is_ajax(request):
        print("Save IS AJAX")
        form = forms.UserFieldForm(request.POST or None)
        name = request.POST.get('name')
        geom = json.loads(request.POST.get('geom'))
        geos = GEOSGeometry(request.POST.get('geom'), srid=4326)
        user = request.user
        instance = models.UserField()
        instance.name = name
        instance.geom_json = geom
        instance.geom = geos
        instance.user = user
        instance.save()
        return JsonResponse({'id': instance.id})
    return redirect('swn:user_dashboard')

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
