from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from . import models
from buek import models as buek_models


from django.db.models import Q
from django.contrib.postgres.fields import JSONField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Column
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django_select2.forms import Select2Widget
from .widgets import SingleRowTextarea

from utilities.widgets import UnitInputWrapper

from crispy_forms.layout import Field, Layout, Row, Column
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

from utilities.forms import InfoLabelFormMixin, CheckboxSelectMultipleWithAttrs, ResultForm



def use_single_row_textarea(field):
    """
    The textbox is 10 lines high by default. This function changes it to a single row.
    """
    if isinstance(field.widget, forms.Textarea):
        field.widget = SingleRowTextarea()
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


class MonicaNewProjectForm(forms.Form):
    project_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control monica-project-name', 'id': 'id_project_name', 'required': 'required',}),
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
        model = models.MonicaProject
        exclude = ['id', 'user']

    def __init__(self, *args, user=None, **kwargs):
        # user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            monica_projects = models.MonicaProject.objects.filter(Q(user=user))
            mp = [( monica_project.monica_model_setup.id, monica_project.name) for monica_project in monica_projects]
            default_setup = models.ModelSetup.objects.filter(is_default=True)[0]
            setup_choices = [(default_setup.id, default_setup.name)] + mp

            self.fields['monica_model_setup'].choices = setup_choices

        self.helper = get_row_form_helper()
        self.helper.layout = Layout(
            Field('name', wrapper_class='row'),
            Field('description', wrapper_class='row'),
            Field('start_date', wrapper_class='row'),
            Field('monica_model_setup', wrapper_class='row'),
        )


class ParametersModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"

        layout_fields = []

        for field_name, field in self.fields.items():
            
            if isinstance(field.widget, (forms.widgets.CheckboxInput, forms.widgets.NullBooleanSelect)):
                layout_fields.append(Field(field_name, css_class='form-check-input mb-3'))
                print("Checkbox field:", field_name)
            else:
                # Replace Textarea with custom Textarea (only two rows not 10)
                if isinstance(field.widget, forms.Textarea):
                    field.widget = SingleRowTextarea()
                layout_fields.append(Field(field_name, wrapper_class='row'))

                self.helper.label_class = 'col-5 col-form-label'
                self.helper.field_class = 'col-7'
        self.helper.layout = Layout(*layout_fields)


            
class CultivarParametersForm(ParametersModelForm):
    
    class Meta:
        model = models.CultivarParameters
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
        model = models.SpeciesParameters
        exclude = ['id', 'user', 'is_default']


class CropResidueParametersForm(ParametersModelForm):
        
    class Meta:
        model = models.CropResidueParameters
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
        model = models.OrganicFertiliser
        exclude = ['id', 'user', 'is_default']

class MineralFertiliserForm(ParametersModelForm):
    class Meta:
        model = models.MineralFertiliser
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
        model = models.UserCropParameters
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
                (instance.id, instance.name) for instance in models.UserCropParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['user_crop_parameters'].choices = [
                (instance.id, instance.name) for instance in models.UserCropParameters.objects.filter(Q(user=user))
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
        model = models.UserEnvironmentParameters
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
            (instance.id, instance.name) for instance in models.MonicaProject.objects.filter(Q(user=user))
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
                (instance.id, instance.name) for instance in models.UserEnvironmentParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['user_environment'].choices = [
                (instance.id, instance.name) for instance in models.UserEnvironmentParameters.objects.filter(Q(user=user))
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
        model = models.UserSoilMoistureParameters
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
                (instance.id, instance.name) for instance in models.UserSoilMoistureParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_moisture'].choices = [
                (instance.id, instance.name) for instance in models.UserSoilMoistureParameters.objects.filter(Q(user=user))
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
        model = models.UserSoilOrganicParameters
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
                (instance.id, instance.name) for instance in models.UserSoilOrganicParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_organic'].choices = [
                (instance.id, instance.name) for instance in models.UserSoilOrganicParameters.objects.filter(Q(user=user))
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
        model = models.SoilTemperatureModuleParameters
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
                (instance.id, instance.name) for instance in models.SoilTemperatureModuleParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_temperature'].choices = [
                (instance.id, instance.name) for instance in models.SoilTemperatureModuleParameters.objects.filter(Q(user=user))
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
        model = models.UserSoilTransportParameters
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
                (instance.id, instance.name) for instance in models.UserSoilTransportParameters.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['soil_transport'].choices = [
                (instance.id, instance.name) for instance in models.UserSoilTransportParameters.objects.filter(Q(user=user))
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
    
    
    class Meta:
        model = models.UserSimulationSettings
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
            instances = models.UserSimulationSettings.objects.filter(Q(user=user) | Q(user=None))
        else:
            instances = models.UserSimulationSettings.objects.filter(Q(user=user))

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
        ('automaticHarvestWorkstep', 'Automatic Harvest'),
        ('nDemandFertilizationWorkstep', 'N Demand Fertilisation'),
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
        model = models.WorkstepSowing 
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
        queryset=models.CultivarParameters.objects.none(),
        label="Cultivar",
        widget=forms.Select(attrs={
            'class': 'form-control form-select cultivar-selector select-parameters cultivar-parameters',
            'workstep-type': 'sowingWorkstep'
        }),
    )

    residue = forms.ModelChoiceField(
        queryset=models.CropResidueParameters.objects.none(),
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
                for instance in models.SpeciesParameters.objects.filter(Q(user=user) | Q(user=None)).order_by('name')
            ]

        self.helper = FormHelper()
        self.helper.label_class = 'col-4 col-form-label'
        self.helper.field_class = 'col-8'
        # self.helper.button_class = 'col-5'
        self.helper.form_tag = False  # Avoids rendering <form> wrapper if you're already in one
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
        queryset = models.MineralFertiliser.objects.all(),
        label="Mineral Fertiliser",
        widget=forms.Select(attrs={
            'class': 'form-control mineral-fertiliser-selector select-parameters mineral-fertiliser-parameters',
            'workstep-type': 'mineralFertilisationWorkstep'
            }),
    )
    class Meta:
        model = models.WorkstepMineralFertilisation 
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
        queryset = models.OrganicFertiliser.objects.all(),
        label="Organic Fertiliser",
        widget=forms.Select(attrs={
            'class': 'form-control organic-fertiliser-selector select-parameters organic-fertiliser-parameters',
            'workstep-type': 'organicFertilisationWorkstep'
            }),
    )
    incorporation = forms.BooleanField()
    class Meta:
        model = models.WorkstepOrganicFertilisation   
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
        model = models.WorkstepTillage
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
        model = models.WorkstepHarvest
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
        model = models.WorkstepIrrigation
        
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



class WorkstepAutomaticHarvestForm(forms.ModelForm): 
    after = forms.ChoiceField(
        choices=[
            ('maturity', 'Maturity'),
            ('anthesis', 'Anthesis'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control automatic-harvest-after select-parameters',
            'workstep-type': 'automaticHarvestWorkstep'
        })
    )
    n_demand = forms.FloatField(min_value=0.0, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector automatic-harvest-n-demand select-parameters',
            'workstep-type': 'automaticHarvestWorkstep'
        }))
    
    class Meta:
        model = models.WorkstepAutomaticHarvest 
        fields = ['date', 'min_percentage_asw', 'max_percentage_asw', 'max_3d_precip_sum', 'max_curr_day_precip']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = get_parameters_form_helper()


class WorkstepNDemandFertilizationForm(forms.ModelForm):
    days = forms.IntegerField(
        initial=7,  
        validators=[
            MinValueValidator(1, message="Days must be at least 1."),
            MaxValueValidator(365, message="Days cannot exceed 365.")
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '365',
            'type': 'number',
            'step': '1',
            'pattern': '[0-9]*'
        })
    )
    after = forms.ChoiceField(
        choices=[
            ('maturity', 'Maturity'),
            ('anthesis', 'Anthesis'),
            ('sowing', 'Sowing'),
            ('harvest', 'Harvest'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control automatic-harvest-after select-parameters',
            'workstep-type': 'nDemandFertilizationWorkstep'
        })
    )
    n_demand = forms.FloatField(min_value=0.0, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector n-demand select-parameters',
            'workstep-type': 'nDemandFertilizationWorkstep'
        }))
    mineral_fertiliser = forms.ModelChoiceField(
        queryset = models.MineralFertiliser.objects.all(),
        label="Mineral Fertiliser",
        widget=forms.Select(attrs={
            'class': 'form-control mineral-fertiliser-selector select-parameters mineral-fertiliser-parameters',
            'workstep-type': 'mineralFertilisationWorkstep'
            }),
    )

    class Meta:
        model = models.WorkstepNDemandFertilization   
        fields = ['date','days', 'after', 'n_demand', 'depth']

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
        self.fields['n_demand'].widget = UnitInputWrapper(widget=self.fields['n_demand'].widget, unit='kg')
        self.fields['depth'].widget = UnitInputWrapper(widget=self.fields['depth'].widget, unit='m')


class SoilProfileSelectionForm(forms.Form):

    PROFILE_SOURCE_CHOICES = (
        ('recommended', 'Recommended soil profile'),
        ('buek', 'BÜK choices'),
        ('user', 'User soil profile'),
        ('scratch', 'Define soil profile from scratch'),
    )

    profile_source = forms.ChoiceField(
        choices=PROFILE_SOURCE_CHOICES,
        widget=forms.RadioSelect,
        initial='recommended',
        label='Soil profile source'
    )

    user_soil_profile = forms.ChoiceField(
        choices=[],
        required=False,
        label='',
        widget=forms.Select(
            attrs={
                'id': 'id_user_soil_profile_selector',
                'class': 'form-select form-select-sm'
            }
        )
    )

    def _radio_with_inline_select(self):
        return format_html(
        """
        <div class="form-check d-flex align-items-center gap-2 mb-2">
            <input class="form-check-input"
                   type="radio"
                   name="profile_source"
                   id="id_profile_source_user"
                   value="user"
                   >

            <label class="form-check-label mb-0"
                   for="id_profile_source_user">
                My soil profile
            </label>

            {}
        </div>
        """,
        self['user_soil_profile']
    )

    def _simple_radio(self, value, checked):
        label = dict(self.PROFILE_SOURCE_CHOICES).get(value, value)
        return f"""
        <div class="form-check mb-2">
            <input class="form-check-input"
                type="radio"
                name="profile_source"
                id="id_profile_source_{value}"
                value="{value}"
                {checked}>

            <label class="form-check-label mb-0"
                for="id_profile_source_{value}">
                {label}
            </label>
        </div>
        """


    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            qs = models.UserSoilProfile.objects.filter(
                Q(user=user) | Q(user=None)
            )
        else:
            qs = models.UserSoilProfile.objects.none()

        self.fields['user_soil_profile'].choices = [
            (obj.id, obj.name) for obj in qs
        ]

        self.helper = get_parameters_form_helper()
        self.helper.layout = Layout(
            HTML(self._simple_radio('recommended', 'checked')),
            HTML(self._simple_radio('buek', '')),
            HTML(self._radio_with_inline_select()),
            HTML(self._simple_radio('scratch', '')),
        )



class UserSoilProfileForm(forms.ModelForm):
    class Meta:
        exclude = ('user',)
        model = models.UserSoilProfile



class UserSoilHorizonForm(forms.ModelForm):
    thickness = forms.FloatField(widget=forms.NumberInput(attrs={'step': 0.1}))
    class Meta:
        model = models.SoilHorizon
        #TODO exclude 'permanent_wilting_point', 'field_capacity', 'bulk_density'??? wilting pt and field cap depend on texture
        exclude = ('user_soil_profile', ) 



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["horizon_no"].widget.attrs["readonly"] = True

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-sm soil-table-input"
            })

        
# Formset for Soil Horizons within an existing Soil Profile. 
# This is used to display or edit existing buek profiles and UserSoilProfiles.
SoilProfileHorizonFormSet = inlineformset_factory(
    models.UserSoilProfile,
    models.SoilHorizon,
    form=UserSoilHorizonForm,
    extra=0,          # allows adding horizons
    can_delete=True,  # allows removing horizons
)



UserSoilHorizonImportFormSet = modelformset_factory(
    models.SoilHorizon,
    form=UserSoilHorizonForm,
    extra=1,
    can_delete=True,
)



class MonicaSiteForm(forms.ModelForm):
    class Meta:
        model = models.MonicaSite
        exclude = ('user', 'is_default', 'site_name', 'soil_profile_content_type', 'soil_profile_object_id', 'soil_profile')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-4 col-form-label'
        self.helper.field_class = 'col-8'
        # self.helper.button_class = 'col-5'
        self.helper.form_tag = False  # Avoids rendering <form> wrapper if you're already in one
        self.helper.layout = Layout(
            # Row(Div(
            #     Field('site_name', wrapper_class='row'),
            #     css_class='col-11 advanced'

            #     ),
                
            # ),
            # Field('date', wrapper_class='row'),
            Row(
                Div(
                    Field('latitude', wrapper_class='row'),
                    css_class='col-11'
                ),
                css_id='latitude-row',
            ),
            Row(
                Div(
                    Field('longitude', wrapper_class='row'),
                    css_class='col-11'
                ),
                css_id='longitude-row',
            ),
            Row(
                Div(
                    Field('altitude', wrapper_class='row'),
                    css_class='col-11 advanced'
                ),
                HTML(
                """
                    <button type="button"  class="btn btn-outline-secondary btn-sm col-1 mb-3 reset get-auto-altitude advanced">
                    <span><i class="bi bi-arrow-clockwise"></i></span>
                    </button>
                """
                ),   
            ),
            Row(
                Div(
                    Field('slope', wrapper_class='row'),
                    css_class='col-11 advanced'
                ),
                HTML(
                """
                    <button type="button"  class="btn btn-outline-secondary btn-sm col-1 mb-3 reset get-auto-slope advanced">
                    <span><i class="bi bi-arrow-clockwise"></i></span>
                    </button>
                """
                ),   
            ),
            Row(
                Div(
                    Field('n_deposition', wrapper_class='row'),
                    css_class='col-11 advanced'
                ),
                HTML(
                """
                    <button type="button"  class="btn btn-outline-secondary btn-sm col-1 mb-3 reset get-auto-n_deposition advanced">
                    <span><i class="bi bi-arrow-clockwise"></i></span>
                    </button>
                """
                ),   
            ),
        )




class MonicaResultDownloadForm(ResultForm): #######
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = (),
        initial='25833',
        required=False,      
    )


    
    probability_raster = forms.MultipleChoiceField(
        label="Wahrscheinlichkeiten",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,  
        choices=[
            ('raster_tif', 'als GeoTIFF Datei'),
        ],
        initial=['raster_tif']
    )

    drainage_network = forms.MultipleChoiceField(
        label="Entwässerungsnetz",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,   
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
        ],
        initial=['shp'],
    )

    drained_areas = forms.MultipleChoiceField(
        label="Entwässerte Flächen",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
        ],
        initial=['shp'],
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='monica', **kwargs)
