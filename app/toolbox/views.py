from django.shortcuts import render
from . import models
from . import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def toolbox_start(request):
    return render(request, 'toolbox/toolbox_start.html')



@login_required
def toolbox_dashboard(request):

    
    user_projects = models.UserProject.objects.filter(user_project__user=request.user)
    toolbox_form = forms.UserProjectForm()

    overlay_lelow_groundwaters = models.BelowGroundWaters.objects.all()
    overlay_above_groundwaters = models.AboveGroundWaters.objects.all()


    data = {
        'sidebar_header': 'Toolbox',
        'user_projects': user_projects,
        'toolbox_form': toolbox_form,
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