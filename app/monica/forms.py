from django import forms
from .models import *
from swn.models import SwnProject

from django.db.models import Q
from django.contrib.postgres.fields import JSONField

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django_select2.forms import Select2Widget
from .widgets import SingleRowTextarea
from django.utils.translation import gettext_lazy as _
from utils.widgets import UnitInputWrapper

from crispy_forms.layout import Field, Layout, Row, Column



def use_single_row_textarea(field):
    """
    The textbox is 10 lines high by default. This function changes it to a single row.
    """
    if isinstance(field.widget, forms.Textarea):
        field.widget = SingleRowTextarea()
        print("is textarea fieldform")
    return field


def get_row_form_helper():
    """
    Defines the layout of Monica forms fields in a row. It requires the loop for field in..."""
    helper = FormHelper()
    helper.label_class = 'col-5 col-form-label'
    helper.field_class = 'col-7'

    return helper

def get_parameters_form_helper():
    helper = FormHelper()
    helper.label_class = 'col-4 col-form-label'
    helper.field_class = 'col-8'
    helper.form_tag = False 
    helper.form_tag = False
    helper.layout = Layout()
    return helper


class MonicaProjectForm(forms.Form):
    project_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_project_name', 'required': 'required',}),
        label='Project Name',
        required=True,
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'id': 'id_project_start_date',
            'class': 'form-control datepicker project-start-datepicker',
            }),   
        input_formats=['%d.%m.%Y'],
        initial = '01.01.' + str(datetime.now().year -1)
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_project_description'}),
        label='Description',
        required=False
    )
    monica_model_setup = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control model-setup-select', 'id': 'id_project_model_setup'}),
        label='Model Setup from other Project',
    )

    class Meta:
        model = MonicaProject
        exclude = ['id', 'user']

    def __init__(self, *args, user=None, **kwargs):
        # user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            print("user is not none")
            monica_projects = MonicaProject.objects.filter(Q(user=user))
            mp = [( monica_project.monica_model_setup.id, monica_project.name) for monica_project in monica_projects]
            default_setup = ModelSetup.objects.filter(is_default=True)[0]
            setup_choices = [(default_setup.id, default_setup.name)] + mp
            print(setup_choices, mp)

            self.fields['monica_model_setup'].choices = setup_choices

        self.helper = get_row_form_helper()
        self.helper.layout = Layout(
            Field('name', wrapper_class='row'),
            Field('description', wrapper_class='row'),
            Field('start_date', wrapper_class='row'),
            Field('monica_model_setup', wrapper_class='row'),
        )


# Use a base class to apply this callback to all forms
class ParametersModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # use_single_row_textarea(field)
            if isinstance(field.widget, forms.Textarea):
                field.widget = SingleRowTextarea()
            # for field_name, field in self.fields.items():
            # if isinstance(field, forms.BooleanField):
            #     # Keep BooleanFields as regular stacked checkboxes
            #     layout_fields.append(
            #         Field(field_name, css_class='form-check-input mb-3')
            #     )
            # else:
            #     # Set label/field alignment only for non-Boolean fields
            #     layout_fields.append(Field(field_name))

            self.helper = FormHelper()
            self.helper.form_method = "post"
            self.helper.label_class = 'col-5 col-form-label'
            self.helper.field_class = 'col-7'

            # Optional: Automatically generate a layout with all fields, each wrapped in a row
            self.helper.layout = Layout(
                *[
                    Field(field_name, wrapper_class='row')
                    for field_name in self.fields
                ]
            )


class CoordinateForm(forms.Form):
    latitude = forms.FloatField(
        max_value=54.92,
        min_value=47.27,
        initial=50.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1})
    )
    longitude = forms.FloatField(
        min_value=5.87,
        max_value=15.04,
        initial=10.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 0.1})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.label_class = 'col-6 col-form-label'
        self.helper.field_class = 'col-6'

        self.helper.layout = Layout(
            Field('latitude', wrapper_class='row'),
            Field('longitude', wrapper_class='row')
        )

            
class CultivarParametersForm(ParametersModelForm):
    
    class Meta:
        model = CultivarParameters
        exclude = ['id', 'user', 'name', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "begin_sensitive_phase_heat_stress": "°C d",
            "critical_temperature_heat_stress": "°C",
            "daylength_requirement": "h", 
            "end_sensitive_phase_heat_stress": "°C d",
            "max_crop_height": "m",
            "optimum_temperature": "°C",
            "specific_leaf_area": "ha/kg",
            "stage_kc_factor": "1;0",
            "stage_temperature_sum": "°C d"
        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)



class SpeciesParametersForm(ParametersModelForm):

    class Meta:
        model = SpeciesParameters
        exclude = ['id', 'user', 'is_default']


class CropResidueParametersForm(ParametersModelForm):
        
    class Meta:
        model = CropResidueParameters
        exclude = ['id', 'user', 'is_default', 'species_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "aom_dry_matter_content": "kg DM/ kg FM",
            "aom_fast_dec_coeff_standard": "d⁻¹",
            "aom_nh4_content": "kg N/ kg DM",
            "aom_no3_content": "kg N/ kg DM",
            "aom_slow_dec_coeff_standard": "d⁻¹",
            "cn_ratio_aom_fast": "25",
            "n_concentration": "kg N/ kg DM",
            "corg_content": "kg C/ kg DM",
            "part_aom_slow_to_smb_fast": "kg/kg",
            "part_aom_slow_to_smb_slow": "kg/kg",
            "part_aom_to_aom_fast": "kg/kg",
            "part_aom_to_aom_slow": "kg/kg",

        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)


class OrganicFertiliserForm(ParametersModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "aom_dry_matter_content": "kg DM/ kg FM",
            "aom_fast_dec_coeff_standard": "d⁻¹",
            "aom_nh4_content": "kg N/ kg DM",
            "aom_no3_content": "kg N/ kg DM",
            "aom_slow_dec_coeff_standard": "d⁻¹",
            # "cn_ratio_aom_fast": "25",
            # "n_concentration": "kg N/ kg DM",
            # "corg_content": "kg C/ kg DM",
            "part_aom_slow_to_smb_fast": "kg/kg",
            "part_aom_slow_to_smb_slow": "kg/kg",
            "part_aom_to_aom_fast": "kg/kg",
            "part_aom_to_aom_slow": "kg/kg",

        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)
    class Meta:
        model = OrganicFertiliser
        exclude = ['id', 'user', 'is_default']

class MineralFertiliserForm(ParametersModelForm):
    class Meta:
        model = MineralFertiliser
        exclude = ['id', 'user', 'is_default', 'type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "carbamid": "kg/kg",
            "nh4": "kg/kg",
            "no3": "kg/kg",
           
        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)


class UserCropParametersForm(ParametersModelForm):
    class Meta:
        model = UserCropParameters
        exclude = ['id', 'user', 'is_default']

    
    


class UserCropParametersSelectionForm(forms.Form):
    user_crop_parameters = forms.ChoiceField(
        choices=[],
        label="User Crop Parameters",
        widget=forms.Select(attrs={'class': 'form-control user-crop-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['user_crop_parameters'].choices = [
                (instance.id, instance.name) for instance in UserCropParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['user_crop_parameters'].choices = [
                (instance.id, instance.name) for instance in UserCropParameters.objects.filter(Q(user=user))
            ]  
        
        self.helper = get_parameters_form_helper()
        self.helper.layout.append(
            Row(
                Div(
                    Field('user_crop_parameters', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="user-crop-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )




class UserEnvironmentParametersForm(ParametersModelForm):
    class Meta:
        model = UserEnvironmentParameters
        exclude = ['id', 'user', 'is_default']


class MonicaProjectSelectionForm(forms.Form):
    monica_project = forms.ChoiceField(
        choices=[],
        label="Monica Projekt",
        widget=forms.Select(attrs={'class': 'form-control monica-project'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monica_project'].choices = [
            (instance.id, instance.name) for instance in MonicaProject.objects.filter(Q(user=user))
        ]
        self.helper = get_row_form_helper()
        self.helper.layout = Layout(
            Field('monica_project', wrapper_class='row')
            
        )




#TODO implement User Environment
class UserEnvironmentParametersSelectionForm(forms.Form):
    user_environment = forms.ChoiceField(
        choices=[],
        label="User Environment Parameters",
        widget=forms.Select(attrs={'class': 'form-control user-environment-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['user_environment'].choices = [
                (instance.id, instance.name) for instance in UserEnvironmentParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['user_environment'].choices = [
                (instance.id, instance.name) for instance in UserEnvironmentParameters.objects.filter(Q(user=user))
            ]

        self.helper = get_parameters_form_helper()
        self.helper.layout.append(
            Row(
                Div(
                    Field('user_environment', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="user-environment-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )


# TODO get all units in the right!!! Not all json files have units. Also, get info buttons for all fields
class UserSoilMoistureParametersForm(ParametersModelForm):                
    class Meta:
        model = UserSoilMoistureParameters
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']

    

class UserSoilMoistureInstanceSelectionForm(forms.Form):
    soil_moisture = forms.ChoiceField(
        choices=[],
        label="Soil Moisture Settings",
        widget=forms.Select(attrs={'class': 'form-control soil-moisture-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['soil_moisture'].choices = [
                (instance.id, instance.name) for instance in UserSoilMoistureParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_moisture'].choices = [
                (instance.id, instance.name) for instance in UserSoilMoistureParameters.objects.filter(Q(user=user))
            ]

        self.helper = get_parameters_form_helper()
        
        self.helper.layout.append(
            Row(
                Div(
                    Field('soil_moisture', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="soil-moisture-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters  advanced">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )


class UserSoilOrganicParametersForm(ParametersModelForm):
    class Meta:
        model = UserSoilOrganicParameters
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "temp_dec_optimal": "°C",
            "moisture_dec_optimal": "%",
            "ammonia_oxidation_rate_coeff_standard": "d⁻²",  # "kg/m³",
            "atmospheric_resistance": "s/m",
            "immobilisation_rate_coeff_nh4": "d⁻²",
            "immobilisation_rate_coeff_no3": "d⁻¹",
            "inhibitor_nh3": "kg·N/m³",
            "limit_clay_effect": "kg/kg",
            "n2o_production_rate": "d⁻¹",
            "nitrite_oxidation_rate_coeff_standard": "d⁻¹",
            "smb_fast_death_rate_standard": "d⁻¹",
            "smb_fast_maint_rate_standard": "d⁻¹",
            "smb_slow_death_rate_standard": "d⁻¹",
            "smb_slow_maint_rate_standard": "d⁻¹",
            "smb_utilization_efficiency": "d⁻¹",
            "som_fast_dec_coeff_standard": "d⁻¹",
            "som_slow_dec_coeff_standard": "d⁻¹",
            "spec_anaerob_denitrification": "g gas-N·g CO₂-C⁻¹",
            "transport_rate_coeff": "d⁻¹",
            "tdenitopt_gauss": "°C",
            "scale_tdenitopt": "°C",
            "kd": "mg NO3-N/L",
            "k_desat": "1/day",
            "fnx": "1/day",
            "vnitmax": "mg NH4-N/kg soil/day",
            "kamm":  "mg NH4-N/L",
            "tnitmin": "°C",
            "tnitopt": "°C",
            "tnitmax": "°C",
            "tnitopt_gauss": "°C",
            "scale_tnitopt": "°C",
            "cmin_pdenit": "%",
            "min_pdenit": "mg N/Kg soil/day",
            "profdenit": "cm",
            "vpotdenit": "kg N/ha/day",
        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)


    
        
class UserSoilOrganicInstanceSelectionForm(forms.Form):
    soil_organic = forms.ChoiceField(
        choices=[],
        label="Soil Organic Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-organic-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['soil_organic'].choices = [
                (instance.id, instance.name) for instance in UserSoilOrganicParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_organic'].choices = [
                (instance.id, instance.name) for instance in UserSoilOrganicParameters.objects.filter(Q(user=user))
            ]

        self.helper = get_parameters_form_helper()
        
        self.helper.layout.append(
            Row(
                Div(
                    Field('soil_organic', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="soil-organic-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )


class SoilTemperatureModuleParametersForm(ParametersModelForm):
    class Meta:
        model = SoilTemperatureModuleParameters
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "base_temperature": "°C",
            "initial_surface_temperature": "°C",
            "density_air": "kg/m³",
            "specific_heat_capacity_air": "J/(kg·K) at 300° K",
            "density_humus": "kg/m³",
            "specific_heat_capacity_humus": "J/(kg·K)",
            "density_water": "kg/m³",
            "specific_heat_capacity_water": "J/(kg·K)",
            "quartz_raw_density": "kg/m³",
            "specific_heat_capacity_quartz": "J/(kg·K)",
        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)



class SoilTemperatureModuleInstanceSelectionForm(forms.Form):
    soil_temperature = forms.ChoiceField(
        choices=[],
        label="Soil Temperature Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-temperature-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['soil_temperature'].choices = [
                (instance.id, instance.name) for instance in SoilTemperatureModuleParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_temperature'].choices = [
                (instance.id, instance.name) for instance in SoilTemperatureModuleParameters.objects.filter(Q(user=user))
            ]
        self.helper = get_parameters_form_helper()
        self.helper.layout.append(
            Row(
                Div(
                    Field('soil_temperature', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="soil-temperature-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )
        


class UserSoilTransportParametersForm(ParametersModelForm):
    class Meta:
        model = UserSoilTransportParameters
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']

    

class UserSoilTransportParametersInstanceSelectionForm(forms.Form):
    soil_transport = forms.ChoiceField(
        choices=[],
        label="Soil Transport Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-transport-parameters'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['soil_transport'].choices = [
                (instance.id, instance.name) for instance in UserSoilTransportParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_transport'].choices = [
                (instance.id, instance.name) for instance in UserSoilTransportParameters.objects.filter(Q(user=user))
            ]
        self.helper = get_parameters_form_helper()
        self.helper.layout.append(
            Row(
                Div(
                    Field('soil_transport', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="soil-transport-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )


class UserSimulationSettingsForm(ParametersModelForm):
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     self.helper = FormHelper()
    #     self.helper.form_tag = False

    #     layout_fields = []

    #     for field_name, field in self.fields.items():
    #         if isinstance(field, forms.BooleanField):
    #             # Keep BooleanFields as regular stacked checkboxes
    #             layout_fields.append(
    #                 Field(field_name, css_class='form-check-input mb-3')
    #             )
    #         else:
    #             # Set label/field alignment only for non-Boolean fields
    #             layout_fields.append(Field(field_name))

    #     # Set horizontal layout classes globally (affects only non-Boolean fields above)
    #     self.helper.label_class = 'col-5 col-form-label'
    #     self.helper.field_class = 'col-7'

    #     self.helper.layout = Layout(*layout_fields)

    
    class Meta:
        model = UserSimulationSettings
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        # Map field names to units
        units = {
            "auto_irrigation_params_amount": "mm",
        }

        for field_name, unit in units.items():
            if field_name in self.fields:
                original_widget = self.fields[field_name].widget
                self.fields[field_name].widget = UnitInputWrapper(widget=original_widget, unit=unit)

        # self.helper = get_parameters_form_helper()
        # self.helper.layout = Layout(
        #     *[
        #         Field(field_name, wrapper_class='row')
        #         for field_name in self.fields
        #     ]
        # )
        # self.helper.layout.append(
        #     Row(
        #         Div(
        #             Field('name', wrapper_class='row'),
        #             css_class='col-11'
        #         ), 
        #         HTML(
        #             """
        #                 <button type="button" data-parameters="user-simulation-settings" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters" data-bs-target="#formModal">
        #                 <span><i class="bi bi-pencil-square"></i></span>
        #                 </button>
        #             """
        #         )
        #     )
        #     )
    

class UserSimulationSettingsInstanceSelectionForm(forms.Form):
    user_simulation_settings = forms.ChoiceField(
        choices=[],
        label="User Simulation Settings",
        widget=forms.Select(attrs={'class': 'form-control user-simulation-settings'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate choices based on user
        if user is not None:
            instances = UserSimulationSettings.objects.filter(Q(user=user) | Q(user=None))
        else:
            instances = UserSimulationSettings.objects.filter(Q(user=user))
        
        self.fields['user_simulation_settings'].choices = [
            (instance.id, instance.name) for instance in instances
        ]
        # TODO when Project load at page load is implemented, this is obsolete
        # Set the default choice to 'default' if it exists
        default_instance = instances.filter(name='default').first()
        if default_instance:
            self.initial['user_simulation_settings'] = default_instance.id

        self.helper = get_parameters_form_helper()
        self.helper.layout = Layout()
        self.helper.layout.append(
            Row(
                Div(
                    Field('user_simulation_settings', wrapper_class='row'),
                    css_class='col-11'
                ), 
                HTML(
                    """
                        <button type="button" data-parameters="user-simulation-settings" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """
                )
            )
            )

class WorkstepSelectorForm(forms.Form):
    WORKSTEP_CHOICES = (
        ('harvestWorkstep', 'Harvest'),
        ('mineralFertilisationWorkstep', 'Mineral Fertilisation'),
        ('organicFertilisationWorkstep', 'Organic Fertilisation'),
        ('tillageWorkstep', 'Tillage'),
        ('irrigationWorkstep', 'Irrigation'),
        )
    workstep_type = forms.ChoiceField(
        choices=WORKSTEP_CHOICES, 
        label='Workstep Type', 
        widget=forms.Select(attrs={'id':'id-workstep-select',
            'class': 'workstep-type-select'
            })
        )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )
        


class WorkstepSowingForm(forms.ModelForm):
    class Meta:
        model = WorkstepSowing 
        fields = ['date', 'species', 'residue', 'cultivar']

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'sowingWorkstep'
        }),
        input_formats=['%d.%m.%Y']
    )

    species = forms.ChoiceField(
        choices=[],
        label="Species",
        widget=forms.Select(attrs={
            'class': 'form-control form-select species-selector select-parameters species-parameters',
            'workstep-type': 'sowingWorkstep'
        }),
    )

    cultivar = forms.ModelChoiceField(
        queryset=CultivarParameters.objects.none(),
        label="Cultivar",
        widget=forms.Select(attrs={
            'class': 'form-control form-select cultivar-selector select-parameters cultivar-parameters',
            'workstep-type': 'sowingWorkstep'
        }),
    )

    residue = forms.ModelChoiceField(
        queryset=CropResidueParameters.objects.none(),
        label="Residues",
        widget=forms.Select(attrs={
            'class': 'form-control form-select crop-residue-selector select-parameters crop-residue-parameters'
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set species choices
        if user is not None:
            self.fields['species'].choices = [('', '---------')] + [
                (instance.id, instance.name)
                for instance in SpeciesParameters.objects.filter(Q(user=user) | Q(user=None)).order_by('name')
            ]

        self.helper = FormHelper()
        self.helper.label_class = 'col-4 col-form-label'
        self.helper.field_class = 'col-8'
        # self.helper.button_class = 'col-5'
        self.helper.form_tag = False  # Avoid rendering <form> wrapper if you're already in one
        self.helper.layout = Layout(
            Row(Div(
                Field('date', wrapper_class='row'),
                css_class='col-11'

                ),
                
            ),
            # Field('date', wrapper_class='row'),
            Row(
                Div(
                    Field('species', wrapper_class='row'),
                    css_class='col-11'
                ),
                HTML(
                """
                    <button type="button" data-parameters="species-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters species-parameters advanced">
                    <span><i class="bi bi-pencil-square"></i></span>
                    </button>
                """
                ),
               
            ),
            Row(
                Div(
                    Field('cultivar', wrapper_class='row'),
                    css_class='col-11'
                ),
                HTML("""
                        <button type="button" data-parameters="cultivar-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters cultivar-parameters advanced">
                        <span><i class="bi bi-pencil-square"></i></span>
                        </button>
                    """),
               
            ),
            Row(
                Div(
                    Field('residue', wrapper_class='row'),
                    css_class='col-11 advanced'
                ),
                HTML(
                """
                    <button type="button" data-parameters="crop-residue-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters crop-residue-parameters advanced">
                    <span><i class="bi bi-pencil-square"></i></span>
                    </button>
                """
                ),
                
            ),
        )
    




class WorkstepMineralFertilisationForm(forms.ModelForm):



    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'mineralFertilisationWorkstep'}),
        input_formats=['%d.%m.%Y']
        )
    amount = forms.FloatField(min_value=0.0, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector mineral-fertiliser-amount select-parameters',
            'workstep-type': 'mineralFertilisationWorkstep'
         }))
    mineral_fertiliser = forms.ModelChoiceField(
        queryset = MineralFertiliser.objects.all(),
        label="Mineral Fertiliser",
        widget=forms.Select(attrs={
            'class': 'form-control mineral-fertiliser-selector select-parameters mineral-fertiliser-parameters',
            'workstep-type': 'mineralFertilisationWorkstep'
            }),
    )
    class Meta:
        model = WorkstepMineralFertilisation 
        fields = ['date', 'amount', 'mineral_fertiliser']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            
            if field_name == 'mineral_fertiliser':
                row_content.append(
                    HTML(
                        """
                            <button type="button" data-parameters="mineral-fertiliser-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters  advanced">
                            <span><i class="bi bi-pencil-square"></i></span>
                            </button>
                        """
                    )
                )
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )
        self.fields['amount'].widget = UnitInputWrapper(widget=self.fields['amount'].widget, unit='kg/ha ???')
        
        

class WorkstepOrganicFertilisationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'organicFertilisationWorkstep'
            }),   
        input_formats=['%d.%m.%Y']
        )
    amount = forms.FloatField(min_value=0.0, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector organic-fertiliser-amount select-parameters',
            'workstep-type': 'organicFertilisationWorkstep'
        }))
    organic_fertiliser = forms.ModelChoiceField(
        queryset = OrganicFertiliser.objects.all(),
        label="Organic Fertiliser",
        widget=forms.Select(attrs={
            'class': 'form-control organic-fertiliser-selector select-parameters organic-fertiliser-parameters',
            'workstep-type': 'organicFertilisationWorkstep'
            }),
    )
    incorporation = forms.BooleanField()
    class Meta:
        model = WorkstepOrganicFertilisation   
        fields = ['date', 'amount', 'organic_fertiliser', 'incorporation']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            
            if field_name == 'organic_fertiliser':
                row_content.append(
                    HTML(
                        """
                            <button type="button" data-parameters="organic-fertiliser-parameters" class="btn btn-outline-secondary btn-sm col-1 mb-3 modify-parameters  advanced">
                            <span><i class="bi bi-pencil-square"></i></span>
                            </button>
                        """
                    )
                )
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )
        self.fields['amount'].widget = UnitInputWrapper(widget=self.fields['amount'].widget, unit='kg/ha ???')


from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import WorkstepTillage

class WorkstepTillageForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'tillageWorkstep'
        }),   
        input_formats=['%d.%m.%Y']
    )

    tillage_depth = forms.IntegerField(
        initial=30,  # Default value
        validators=[
            MinValueValidator(1, message="Tillage depth must be at least 1."),
            MaxValueValidator(100, message="Tillage depth cannot exceed 100.")
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '100',
            'type': 'number',
            'step': '1',
            'pattern': '[0-9]*'        })
    )

    class Meta:
        model = WorkstepTillage
        fields = ['date', 'tillage_depth']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )
        self.fields['tillage_depth'].widget = UnitInputWrapper(widget=self.fields['tillage_depth'].widget, unit='cm')



class WorkstepHarvestForm(forms.ModelForm):
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'harvestWorkstep'
            }),  
        input_formats=['%d.%m.%Y']
        )
    class Meta:
        model = WorkstepHarvest
        fields = ['date']
        widgets = {
            'date': forms.DateInput(),
        }
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )


class WorkstepIrrigationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'irrigationWorkstep'
            }),   
        input_formats=['%d.%m.%Y']
        )
    amount = forms.FloatField(
        min_value=0.0, 
        initial=20.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector irrigation-amount select-parameters',
            'workstep-type': 'irrigationWorkstep'
            }))
    
    class Meta:
        model = WorkstepIrrigation
        
        fields = ['date', 'amount']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()
        for field_name in self.fields:
            row_content = [

                    Div(
                        Field(field_name, wrapper_class='row'),
                        css_class='col-11'
                    ),     
            ]
            self.helper.layout.append(
                Row(
                    *row_content
                )
            )
        self.fields['amount'].widget = UnitInputWrapper(widget=self.fields['amount'].widget, unit='mm')





