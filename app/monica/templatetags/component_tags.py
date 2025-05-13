from django.template import Library


register = Library()

@register.inclusion_tag('monica/monica_model_tab_project.html', takes_context=True)
def render_tab_project(
    context, 
    project_form,
    user_environment_parameters_select_form, 
    user_crop_parameters_select_form,
    user_simulation_settings_select_form):
    context.update({
        'project_form': project_form,
        'user_environment_parameters_select_form': user_environment_parameters_select_form,
        'user_crop_parameters_select_form': user_crop_parameters_select_form,
        'user_simulation_settings_select_form': user_simulation_settings_select_form,
    })
    return context

    

@register.inclusion_tag('monica/monica_model_tab_general_parameters.html', takes_context=True)
def render_tab_general_parameters(context, coordinate_form):
    """
    Render the 'monica/monica_model_tab_general_parameters.html' template.
    """
    context.update({
        'coordinate_form': coordinate_form,
    })


    return {'coordinate_form': coordinate_form}



@register.inclusion_tag('monica/monica_model_tab_crop_rotation.html', takes_context=True)
def render_tab_crop_rotation(context):
    
    return context

@register.inclusion_tag('monica/monica_model_tab_soil.html', takes_context=True)
def render_tab_soil(
    context,
    user_soil_moisture_select_form,
    user_soil_organic_select_form,
    soil_temperature_module_selection_form,
    user_soil_transport_parameters_selection_form
    ):
    
    context.update({
        'user_soil_moisture_select_form': user_soil_moisture_select_form,
        'user_soil_organic_select_form': user_soil_organic_select_form,
        'soil_temperature_module_selection_form': soil_temperature_module_selection_form,
        'user_soil_transport_parameters_selection_form': user_soil_transport_parameters_selection_form,
    })
    return context


@register.inclusion_tag('monica/monica_model_tab_result.html', takes_context=True)
def render_tab_result(context):
    """
    Render the 'monica/monica_model_tab_result.html' template.
    """

    return context

