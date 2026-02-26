from django.template import Library


register = Library()

@register.inclusion_tag('monica/monica_model_tab_project.html', takes_context=True)
def render_tab_project(
    context, 
    user_environment_parameters_select_form, 
    user_crop_parameters_select_form,
    user_simulation_settings_select_form
    ):
    request = context.get('request')
    project_select_form = context.get('project_select_form')
    new_project_form = context.get('new_project_form')

    context = {
        'request': request,
        'project_select_form': project_select_form,
        'new_project_form': new_project_form,
        'user_environment_parameters_select_form': user_environment_parameters_select_form,
        'user_crop_parameters_select_form': user_crop_parameters_select_form,
        'user_simulation_settings_select_form': user_simulation_settings_select_form,
    }
    return context

    





@register.inclusion_tag('monica/monica_model_tab_crop_rotation.html', takes_context=True)
def render_tab_crop_rotation(context):
    
    return context

@register.inclusion_tag('monica/monica_model_tab_site.html', takes_context=True)
def render_tab_soil(
    context,
    site_form,
    user_soil_profile_select_form,
    user_soil_profile_form,
    user_soil_moisture_select_form,
    user_soil_organic_select_form,
    soil_temperature_module_selection_form,
    user_soil_transport_parameters_selection_form
    ):
    request = context.get('request')
    context = {
        'request': request,
        'site_form': site_form,
        'user_soil_profile_select_form': user_soil_profile_select_form,
        'user_soil_profile_form': user_soil_profile_form,
        'user_soil_moisture_select_form': user_soil_moisture_select_form,
        'user_soil_organic_select_form': user_soil_organic_select_form,
        'soil_temperature_module_selection_form': soil_temperature_module_selection_form,
        'user_soil_transport_parameters_selection_form': user_soil_transport_parameters_selection_form,
    }
    return context


@register.inclusion_tag('monica/monica_model_tab_result.html', takes_context=True)
def render_tab_result(context):
    """
    Render the 'monica/monica_model_tab_result.html' template.
    """

    return context

