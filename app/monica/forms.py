from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from django.db.models import Q
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.contrib.postgres.fields import JSONField

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django_select2.forms import Select2Widget
from .widgets import SingleRowTextarea
from django.utils.translation import gettext_lazy as _
from utils.widgets import UnitInputWrapper



def use_single_row_textarea(field):
    """
    The textbox is 10 lines high by default. This function changes it to a single row.
    """
    if isinstance(field.widget, forms.Textarea):
        field.widget = SingleRowTextarea()
        print("is textarea fieldform")
    return field


class MonicaProjectForm(forms.Form):
    project_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_project_name'}),
        label='Project Name',
        required=True
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

    def __init__(self, *args, user=9, **kwargs):
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


# Use a base class to apply this callback to all forms
class ParametersModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            use_single_row_textarea(field)

class CoordinateForm(forms.Form):
    latitude = forms.FloatField(
        max_value=54.92,
        min_value=47.27,
        initial = 50.00,
        widget=forms.NumberInput(attrs={'class': 'form-control',  'step': 0.1})
    )
    longitude = forms.FloatField(
        min_value = 5.87,
        max_value = 15.04,
        initial = 10.00,
        widget=forms.NumberInput(attrs={'class': 'form-control',  'step': 0.1})
    )

            
class CultivarParametersForm(ParametersModelForm):
    
    class Meta:
        model = CultivarParameters
        exclude = ['id', 'user', 'name', 'is_default']

class CultivarParametersInstanceSelectForm(forms.ModelForm):
    cultivar = forms.ChoiceField(
        choices=[],
        label="Cultivar",
        widget=forms.Select(attrs={'class': 'form-control form-select cultivar-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cultivar'].choices = [
            (instance.id, instance.name) for instance in CultivarParameters.objects.all()
        ]



class SpeciesParametersForm(ParametersModelForm):

    class Meta:
        model = SpeciesParameters
        exclude = ['id', 'user', 'is_default']



class CultivarAndSpeciesSelectionForm(forms.Form):
    """
    This is the old selection form used in SWN field edit.
    Can be deleted once Monica is incorporated into SWN.
    """
    species_parameters = forms.ModelChoiceField(queryset=SpeciesParameters.objects.all(), label="Feldkultur", empty_label="Select Species")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cultivar_parameters'] = forms.ModelChoiceField(queryset=CultivarParameters.objects.none(), label="Kultursorte", empty_label="Select Cultivar")

class CropResidueParametersForm(ParametersModelForm):
        
    class Meta:
        model = CropResidueParameters
        exclude = ['id', 'user', 'is_default', 'species_name']

class OrganicFertiliserForm(ParametersModelForm):
    class Meta:
        model = OrganicFertiliser
        exclude = ['id', 'user', 'is_default']

class MineralFertiliserForm(ParametersModelForm):
    class Meta:
        model = MineralFertiliser
        exclude = ['id', 'user', 'is_default', 'type']


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



class UserEnvironmentParametersForm(ParametersModelForm):
    class Meta:
        model = UserEnvironmentParameters
        exclude = ['id', 'user', 'is_default']


class MonicaProjectSelectionForm(forms.Form):
    monica_project = forms.ChoiceField(
        choices=[],
        label="Monica Project",
        widget=forms.Select(attrs={'class': 'form-control monica-project'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['monica_project'].choices = [
            (instance.id, instance.name) for instance in MonicaProject.objects.filter(Q(user=user))
        ]
        


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


class UserSoilOrganicParametersForm(forms.ModelForm):
    class Meta:
        model = UserSoilOrganicParameters
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']
        
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


class SoilTemperatureModuleParametersForm(forms.ModelForm):
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
            "specific_heat_capacity_air": "J/(kg·K)",
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


class UserSoilTransportParametersForm(forms.ModelForm):
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


class UserSimulationSettingsForm(forms.ModelForm):
    
    class Meta:
        model = UserSimulationSettings
        field_order = ['name']
        exclude = ['id', 'user', 'is_default']
    

class UserSimulationSettingsInstanceSelectionForm(forms.Form):
    user_simulation_settings = forms.ChoiceField(
        choices=[],
        label="User Simulation Settings",
        widget=forms.Select(attrs={'class': 'form-control user-simulation-settings'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['user_simulation_settings'].choices = [
                (instance.id, instance.name) for instance in UserSimulationSettings.objects.filter(Q(user=user) | Q(user=None))
            ]
        else:
            self.fields['user_simulation_settings'].choices = [
                (instance.id, instance.name) for instance in UserSimulationSettings.objects.filter(Q(user=user))
            ]


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

class WorkstepSowingForm(forms.ModelForm):
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
        label="Residue Parameters",
        widget=forms.Select(attrs={'class': 'form-control form-select crop-residue-selector select-parameters crop-residue-parameters'}),
        )

    class Meta:
        model = WorkstepSowing
        fields = ['species', 'cultivar', 'date', 'plant_density']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['species'].choices = [('', '---------')] + [
                (instance.id, instance.name) for instance in SpeciesParameters.objects.filter(Q(user=user) | Q(user=None)).order_by('name')
            ]


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


class WorkstepTillageForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker workstep-datepicker',
            'workstep-type': 'tillageWorkstep'
            }),   
        input_formats=['%d.%m.%Y']
        )
    class Meta:
        model = WorkstepTillage
        fields = ['date', 'tillage_depth']
        widgets = {
            'date': forms.DateInput(),
        }


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
        widget=forms.NumberInput(attrs={
            'class': 'form-control number-selector irrigation-amount select-parameters',
            'workstep-type': 'irrigationWorkstep'
            }))
    class Meta:
        model = WorkstepIrrigation
        
        fields = ['date', 'amount']




