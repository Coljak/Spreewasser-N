from django.shortcuts import render
from . import models
from . import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
import json

# Create your views here.
def toolbox_start(request):
    return render(request, 'toolbox/toolbox_start.html')



@login_required
def toolbox_dashboard(request):
    user_projects = models.UserProject.objects.filter(user_project__user=request.user)
    toolbox_form = forms.UserProjectForm()

    overlay_lelow_groundwaters = models.BelowGroundWaters.objects.all()
    overlay_above_groundwaters = models.AboveGroundWaters.objects.all()

    outline_injection = json.loads(GEOSGeometry(models.OutlineInjection.objects.all()[0].geom).geojson)
    outline_infiltration = json.loads(GEOSGeometry(models.OutlineInfiltration.objects.all()[0].geom).geojson)
    outline_surface_water = json.loads(GEOSGeometry(models.OutlineSurfaceWater.objects.all()[0].geom).geojson)
    outline_geste = json.loads(GEOSGeometry(models.OutlineGeste.objects.all()[0].geom).geojson)

    # projectregion = models.ProjectRegion.objects.all()
    # geometry = GEOSGeometry(projectregion[0].geom)
    # geojson = json.loads(geometry.geojson)

    data = {
        'sidebar_header': 'Toolbox',
        'user_projects': user_projects,
        'toolbox_form': toolbox_form,
        'outline_injection': outline_injection,
        'outline_infiltration': outline_infiltration,
        'outline_surface_water': outline_surface_water,
        'outline_geste': outline_geste
    }
    # user_projects = []

    # for user_project in user_projects:
    #     if request.user == user_project.user:
    #         item = {
    #             'name': user_project.name,
    #             'user_name': user_project.user.name,
    #             'description': user_project.description,
    #         }
    #         user_projects.append(item)



    return JsonResponse(data)