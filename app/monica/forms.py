from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from bootstrap_datepicker_plus.widgets import DatePickerInput

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class DateInput(forms.DateInput):
    input_type = 'date'
    localize = False
    input_formats=['%d.%m.%Y']
    format = '%d.%m.%Y'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)

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

            
class CultivarParametersForm(forms.ModelForm):
    
    class Meta:
        model = CultivarParameters
        exclude = ['id', 'user', 'is_default']

class SpeciesParametersForm(forms.ModelForm):

    class Meta:
        model = SpeciesParameters
        exclude = ['id', 'user', 'is_default']

class CultivarAndSpeciesSelectionForm(forms.Form):
    species_parameters = forms.ModelChoiceField(queryset=SpeciesParameters.objects.all(), label="Feldkultur", empty_label="Select Species")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cultivar_parameters'] = forms.ModelChoiceField(queryset=CultivarParameters.objects.none(), label="Kultursorte", empty_label="Select Cultivar")

class CropResidueParametersForm(forms.ModelForm):
        
        class Meta:
            model = CropResidueParameters
            exclude = ['id', 'user', 'is_default']

class OrganicFertiliserForm(forms.ModelForm):
    class Meta:
        model = OrganicFertiliser
        exclude = ['id', 'user', 'is_default']

class MineralFertiliserForm(forms.ModelForm):
    class Meta:
        model = MineralFertiliser
        exclude = ['id', 'user', 'is_default']


class UserCropParametersForm(forms.ModelForm):
    class Meta:
        model = UserCropParameters
        exclude = ['id', 'user', 'is_default']


class UserCropParametersSelectionForm(forms.Form):
    instance_id = forms.ChoiceField(
        choices=[],
        label="User Crop Parameters",
        widget=forms.Select(attrs={'class': 'form-control crop-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instance_id'].choices = [
            (instance.id, instance.name) for instance in UserCropParameters.objects.all()
        ]


class UserEnvironmentParametersForm(forms.ModelForm):
    class Meta:
        model = UserEnvironmentParameters
        exclude = ['id', 'user', 'is_default']

class UserEnvironmentParametersSelectionForm(forms.Form):
    instance_id = forms.ChoiceField(
        choices=[],
        label="User Environment Settings",
        widget=forms.Select(attrs={'class': 'form-control environment-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instance_id'].choices = [
            (instance.id, instance.name) for instance in UserEnvironmentParameters.objects.all()
        ]


class UserSoilMoistureParametersForm(forms.ModelForm):                
    class Meta:
        model = UserSoilMoistureParameters
        exclude = ['id', 'user', 'is_default']

class UserSoilMoistureInstanceSelectionForm(forms.Form):
    soil_moisture = forms.ChoiceField(
        choices=[],
        label="Soil Moisture Settings",
        widget=forms.Select(attrs={'class': 'form-control soil-moisture-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soil_moisture'].choices = [
            (instance.id, instance.name) for instance in UserSoilMoistureParameters.objects.all()
        ]


class UserSoilOrganicParametersForm(forms.ModelForm):
    class Meta:
        model = UserSoilOrganicParameters
        exclude = ['id', 'user']
        
class UserSoilOrganicInstanceSelectionForm(forms.Form):
    soil_organic = forms.ChoiceField(
        choices=[],
        label="Soil Organic Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-organic-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soil_organic'].choices = [
            (instance.id, instance.name) for instance in UserSoilOrganicParameters.objects.all()
        ]


class SoilTemperatureModuleParametersForm(forms.ModelForm):
    class Meta:
        model = SoilTemperatureModuleParameters
        exclude = ['id', 'user']

class SoilTemperatureModuleInstanceSelectionForm(forms.Form):
    soil_temperature = forms.ChoiceField(
        choices=[],
        label="Soil Temperature Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-temperature-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soil_temperature'].choices = [
            (instance.id, instance.name) for instance in SoilTemperatureModuleParameters.objects.all()
        ]


class UserSoilTransportParametersForm(forms.ModelForm):
    class Meta:
        model = UserSoilTransportParameters
        exclude = ['id', 'user', 'is_default']

class UserSoilTransportParametersInstanceSelectionForm(forms.Form):
    soil_transport = forms.ChoiceField(
        choices=[],
        label="Soil Transport Parameters",
        widget=forms.Select(attrs={'class': 'form-control soil-transport-parameters'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soil_transport'].choices = [
            (instance.id, instance.name) for instance in UserSoilTransportParameters.objects.all()
        ]


class UserSimulationSettingsForm(forms.ModelForm):
    name = forms.ModelChoiceField(
        queryset=UserSimulationSettings.objects.all().values_list('name', flat=True),
        widget=forms.Select,
        required=False,
        label="Simulation Setting",
        empty_label=None
    )
    class Meta:
        model = UserSimulationSettings
        exclude = ['id', 'user']
        
    def __init__(self, *args, **kwargs):
        super(UserSimulationSettingsForm, self).__init__(*args, **kwargs)
        # Set the default value to the one named 'default'
        try:
            default_setting = UserSimulationSettings.objects.get(default=True)
            self.fields['name'].initial = default_setting
        except UserSimulationSettings.DoesNotExist:
            self.fields['name'].initial = None

class UserSimulationSettingsInstanceSelectionForm(forms.Form):
    user_simulation_settings = forms.ChoiceField(
        choices=[],
        label="User Simulation Settings",
        widget=forms.Select(attrs={'class': 'form-control simulation-settings'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_simulation_settings'].choices = [
            (instance.id, instance.name) for instance in UserSimulationSettings.objects.all()
        ]


class WorkstepSelectorForm(forms.Form):
    WORKSTEP_CHOICES = (
        ('workstep-harvest-template', 'Harvest'),
        ('workstep-mineral-fertilization-template', 'Mineral Fertilization'),
        ('workstep-organic-fertilization-template', 'Organic Fertilization'),
        ('workstep-tillage-template', 'Tillage'),
        )
    workstep_type = forms.ChoiceField(
        choices=WORKSTEP_CHOICES, 
        label='Workstep Type', 
        widget=forms.Select(attrs={'class': 'workstep-type-select'})
        )

class WorkstepSowingForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), input_formats=['%d.%m.%Y'])
    species = forms.ModelChoiceField(
        queryset=SpeciesParameters.objects.all(),
          label="Species",
          widget=forms.Select(attrs={'class': 'form-control, species-selector'}),
          )
    cultivar = forms.ModelChoiceField(
        queryset=CultivarParameters.objects.none(),
        label="Cultivar",
        widget=forms.Select(attrs={'class': 'form-control, cultivar-selector'}),
        )

    class Meta:
        model = WorkstepSowing
        fields = ['species', 'cultivar', 'date', 'plant_density']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['species'].queryset = SpeciesParameters.objects.all()
        # self.fields['cultivar'].queryset = CultivarParameters.objects.none()

        if 'species' in self.data:
            try:
                species_id = int(self.data.get('species'))
                self.fields['cultivar'].queryset = CultivarParameters.objects.filter(species_parameters_id=species_id).order_by('species_name')
            except (ValueError, TypeError):
                pass  # invalid input; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields['cultivar'].queryset = self.instance.species.cultivarparameters_set.order_by('species_name')

class WorkstepMineralFertilizationForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), input_formats=['%d.%m.%Y'])
    class Meta:
        model = WorkstepMineralFertilization
        fields = ['date', 'amount', 'mineral_fertiliser']

class WorkstepOrganicFertilizationForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}), input_formats=['%d.%m.%Y'])
    class Meta:
        model = WorkstepOrganicFertilization
        fields = ['date', 'amount', 'organic_fertiliser', 'incorporation']
        widgets = {
            'date': DateInput(),
        }
        
#     def save(self, commit=False):
#         instance = super().save(commit=False)
#         instance.date = self.cleaned_data['date']
#         instance.amount = self.cleaned_data['amount']
#         instance.organic_fertiliser = self.cleaned_data['organic_fertiliser']
#         instance.incorporation = self.cleaned_data['incorporation']
#         if commit:
#             instance.save
#         return instance

class WorkstepTillageForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd.mm.yyyy'}), input_formats=['%d.%m.%Y'])
    class Meta:
        model = WorkstepTillage
        fields = ['date', 'tillage_depth']
        widgets = {
            'date': DateInput(),
        }
#     def save(self, commit=False):
#         instance = super().save(commit=False)
#         instance.date = self.cleaned_data['date']
#         instance.tillage_depth = self.cleaned_data['tillage_depth']
#         if commit:
#             instance.save
#         return instance



class WorkstepHarvestForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd.mm.yyyy', 'type': 'date'}), input_formats=['%d.%m.%Y'])
    class Meta:
        model = WorkstepHarvest
        fields = ['date']
        widgets = {
            'date': DateInput(),
        }

#     def save(self, commit=False):
#         instance = super().save(commit=False)
#         instance.date = self.cleaned_data['date']
#         if commit:
#             instance.save
#         return instance








