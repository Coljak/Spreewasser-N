from django.http import JsonResponse
from monica.models import *
from swn.models import SwnProject, UserField
from buek.models import SoilProfile
from datetime import datetime
import json



def save_project(project_data, user, project_class=MonicaProject):
# def save_project(request, project_class=MonicaProject, project_id=None):
    """
    Reusable logic to save a project.
    :param request: Django request object
    :param project_class: Model class to use for saving the project
    :return: JsonResponse
    """
    # if request.method == 'POST':
    #     user = request.user
        
    #     data = json.loads(request.body)
    data = project_data
    print('is POST', data)


    def verify_unique_name(name):
        user_project_names = [proj.name for proj in project_class.objects.filter(user=user)]  
        counter = 0
        while name in user_project_names:
            name += f' (new-{counter})'
            counter += 1
        return name
    
    
    # modify project
    if project_data.get('id', None):
        project_id = project_data.get('id')
        print('Monica Modify Project')
        project = project_class.objects.get(id=project_id)
        if user != project.user:
            return JsonResponse({'message': {'success': False, 'message': 'You are not allowed to edit this project'}})
        if project.name != data.get('name'):
            project.name = verify_unique_name(data.get('name'))

        project.start_date = data.get('startDate')
        project.description = data.get('description')
        

        
        # save the site
        try:
            project.monica_site.latitude = data.get('latitude')
            project.monica_site.longitude = data.get('longitude')
            project.monica_site.altitude = data.get('altitude', 0)
            project.monica_site.n_deposition = data.get('n_deposition', 11)
            soil_profile_source = data.get('soilProfileSource')
            if soil_profile_source == 'buek':
                soil_profile = SoilProfile.objects.get(pk=data.get('buekSoilProfileId'))
            elif soil_profile_source == 'userSoilProfile':
                soil_profile = UserSoilProfile.objects.get(pk=data.get('userSoilProfileId'))
            project.monica_site.soil_profile = soil_profile
            project.monica_site.save()
        except:
            errormessage = "Error saving soil profile."

        # save the model setup
        # monica_model_setup = ModelSetup.objects.get(id=data.get('modelSetupId'))
        project.monica_model_setup.name = data.get('modelSetupName', '')

        user_crop_parameters = UserCropParameters.objects.get(pk=data.get('userCropParametersId'))
        print("data.get('userCropParametersId')", data.get('userCropParametersId'))
        print("user_crop_parameters", user_crop_parameters)
        project.monica_model_setup.user_crop_parameters = user_crop_parameters

        user_environment_parameters = UserEnvironmentParameters.objects.get(pk=data.get('userEnvironmentParametersId'))
        project.monica_model_setup.user_environment_parameters = user_environment_parameters

        user_soil_moisture_parameters = UserSoilMoistureParameters.objects.get(pk=data.get('userSoilMoistureParametersId'))
        project.monica_model_setup.user_soil_moisture_parameters = user_soil_moisture_parameters

        user_soil_transport_parameters = UserSoilTransportParameters.objects.get(pk=data.get('userSoilTransportParametersId'))
        print("data.get('userSoilTransportParametersId')", data.get('userSoilTransportParametersId'))
        print("user_soil_transport_parameters", user_soil_transport_parameters)
        project.monica_model_setup.user_soil_transport_parameters = user_soil_transport_parameters

        user_soil_organic_parameters = UserSoilOrganicParameters.objects.get(pk=data.get('userSoilOrganicParametersId'))
        project.monica_model_setup.user_soil_organic_parameters = user_soil_organic_parameters
        
        user_soil_temperature_parameters = SoilTemperatureModuleParameters.objects.get(pk=data.get('userSoilTemperatureParametersId'))
        project.monica_model_setup.user_soil_temperature_parameters = user_soil_temperature_parameters

        simulation_parameters = UserSimulationSettings.objects.get(pk=data.get('userSimulationSettingsId'))
        project.monica_model_setup.simulation_parameters = simulation_parameters

        project.monica_model_setup.crop_rotation = data.get('rotation')
        project.monica_model_setup.save()
        
        
        # TODO  add additional fields of medel setup
    # save new project
    else:
        project = project_class()
        print('Monica Save new Project')
        
        project.name = verify_unique_name(data.get('name'))
        project.user = user
        project.creation_date = datetime.now()

        # new model setup
        monica_model_setup = ModelSetup.objects.get(id=data.get('modelSetupId'))
        monica_model_setup.pk = None
        monica_model_setup.user = user
        monica_model_setup.is_default = False
        monica_model_setup.save()
        project.monica_model_setup = monica_model_setup

        if project_class == SwnProject:
            print('additional fields', data.get('userField'))
            project.user_field = UserField.objects.get(pk=data.get('userField'))

        # new site
        # monica
        monica_site = MonicaSite(user=project.user)
        monica_site.save()
        project.monica_site = monica_site

    project.start_date = data.get('startDate').split('T')[0]
    project.description = data.get('description')
    

    project.save()

    return project

