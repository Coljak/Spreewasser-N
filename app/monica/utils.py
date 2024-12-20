from django.http import JsonResponse
from monica.models import MonicaProject, ModelSetup
from datetime import datetime
import json

def save_project(request, project_class=MonicaProject, additional_fields=None):
    """
    Reusable logic to save a project.
    :param request: Django request object
    :param project_class: Model class to use for saving the project
    :param additional_fields: A dict of extra fields to add to the project
    :return: JsonResponse
    """
    if request.method == 'POST':
        user = request.user
        
        data = json.loads(request.body)
        print('is POST', data)
        project_id=data.get('project_id', None)

        def verify_unique_name(name):
            user_project_names = [proj.name for proj in project_class.objects.filter(user=user)]  
            counter = 0
            while name in user_project_names:
                name += f' (new-{counter})'
                counter += 1
            return name
        
        project = project_class()
        if project_id:
            project = project_class.objects.get(id=project_id)
            if user != project.user:
                return JsonResponse({'message': {'success': False, 'message': 'You are not allowed to edit this project'}})
            if project.name != data.get('name'):
                project.name = verify_unique_name(data.get('name'))

            # TODO  add additional fields of medel setup

        else:
            project.name = verify_unique_name(data.get('name'))
            project.user = user
            project.creation_date = datetime.now()

            # new model setup
            monica_model_setup = ModelSetup.objects.get(id=data.get('modelSetup'))
            monica_model_setup.pk = None
            monica_model_setup.user = user
            monica_model_setup.is_default = False
            monica_model_setup.save()
            project.monica_model_setup = monica_model_setup

        project.start_date = data.get('startDate').split('T')[0]
        project.description = data.get('description')
        

        project.save()

        return project

