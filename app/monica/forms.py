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

class CultivarParametersForm(forms.Form):
    species_parameters = forms.ModelChoiceField(queryset=SpeciesParameters.objects.all(), label="Feldkultur", empty_label="Select Species")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cultivar_parameters'] = forms.ModelChoiceField(queryset=CultivarParameters.objects.none(), label="Kultursorte", empty_label="Select Cultivar")

class WorkstepSowingForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), input_formats=['%d.%m.%Y'])

    class Meta:
        model = WorkstepSowing
        fields = ['species', 'cultivar', 'date', 'plant_density']
        widgets = {
            'date': forms.DateInput(),
        }
          

    def save(self, commit=False):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.species = self.cleaned_data['species']
        instance.cultivar = self.cleaned_data['cultivar']
        instance.plant_density = self.cleaned_data['plant_density']
        instance.residue_parameters = CropResidueParameters.objects.get(species_parameters=instance.species)
        if commit:
            instance.save
        return instance



class WorkstepMineralFertilizationForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput(), input_formats=['%d.%m.%Y'])
    class Meta:
        model = WorkstepMineralFertilization
        fields = ['date', 'amount', 'mineral_fertiliser']

    def save(self, commit=False):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.amount = self.cleaned_data['amount']
        instance.mineral_fertiliser = self.cleaned_data['mineral_fertiliser']
        if commit:
            instance.save
        return instance
        

class WorkstepOrganicFertilizationForm(forms.ModelForm):
    class Meta:
        model = WorkstepOrganicFertilization
        fields = ['date', 'amount', 'organic_fertiliser', 'incorporation']
        widgets = {
            'date': DateInput(),
        }
        
    def save(self, commit=False):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.amount = self.cleaned_data['amount']
        instance.organic_fertiliser = self.cleaned_data['organic_fertiliser']
        instance.incorporation = self.cleaned_data['incorporation']
        if commit:
            instance.save
        return instance

class WorkstepTillageForm(forms.ModelForm):
    class Meta:
        model = WorkstepTillage
        fields = ['date', 'tillage_depth']
        widgets = {
            'date': DateInput(),
        }
    def save(self, commit=False):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        instance.tillage_depth = self.cleaned_data['tillage_depth']
        if commit:
            instance.save
        return instance



class WorkstepHarvestForm(forms.ModelForm):
    class Meta:
        model = WorkstepHarvest
        fields = ['date']
        widgets = {
            'date': DateInput(),
        }

    def save(self, commit=False):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        if commit:
            instance.save
        return instance




