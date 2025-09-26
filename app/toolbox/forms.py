from django import forms
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max, Min, NOT_PROVIDED
from . import models
# from .utils import widgets
from django.db.models import Q

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, StrictButton
from django_filters.fields import RangeField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.gis.geos import GEOSGeometry

from utils.widgets import CustomRangeSliderWidget, CustomSingleSliderWidget,CustomSimpleSliderWidget, CustomDoubleSliderWidget



  
class SliderFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2 col-md-2 col-sm-auto'
        self.helper.field_class = 'col-lg-10 col-md-10 col-sm-auto'

        self.helper.layout = Layout(*[Field(name) for name in self.fields])


class ToolboxProjectSelectionForm(forms.Form):
    toolbox_project = forms.ChoiceField(
        choices=[],
        label="Toolbox Project",
        widget=forms.Select(attrs={'class': 'form-control toolbox-project'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['toolbox_project'].choices = [
            # print(instance.id, instance.name) for instance in ToolboxProject.objects.filter(Q(user=user))
            (instance.id, instance.name) for instance in models.ToolboxProject.objects.filter(Q(user=user))
        ]



class ToolboxProjectForm(forms.Form):
    user_field = forms.ModelChoiceField(
        queryset=models.UserField.objects.all(),
        label='Field',
        widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
    )
    project_type = forms.ModelChoiceField(
        queryset = models.ToolboxType.objects.all(),
        label='Project Type',
        empty_label=None,
        widget=forms.Select(attrs={'id': 'projectTypeSelect', 'class': 'project-type-dropdown'}),
    )
    project_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_project_name', 'required': 'required',}),
        label='Project Name',
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_project_description'}),
        label='Description',
        required=False
    )

    class Meta:
        model = models.ToolboxProject
        exclude = ['id', 'user']

class OverallWeightingsForm(forms.Form):
    overall_usability = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_overall_usability",
            "name": "weighting_overall_usability",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 20,
            "data_default_value": 20,
            "units": "%",
        }),
        label="Gewichtung der allgemeine Nutzbarkeit",
        help_text=(
            "Die allgemeine Nutzbarkeit ist eine Bewertung der Eignung des Standorts für "
            "Versickerungsmaßnahmen. Eine hohe Bewertung begünstigt Versickerungsmaßnahmen."
        )
    )

    soil_index = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_soil_index",
            "name": "weighting_soil_index",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 80,
            "data_default_value": 80,
            "units": "%",
        }),
        label="Gewichtung der Bodenbewertung",
        help_text=(
            "Gewichtung der Bodenbewertung ist eine Bewertung der Eignung des Standorts für "
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'overall-weighting-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'overall-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'))


      
class WeightingsForestForm(forms.Form):
    field_capacity = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_field_capacity",
            "name": "weighting_forest_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
            
        }),
        label="Feldkapazität (%)",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydraulic_conductivity_1m = forms.IntegerField(
        min_value=0,
        max_value=100,
        # initial=33,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_hydraulic_conductivity_1m",
            "name": "weighting_forest_hydraulic_conductivity_1m",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydraulische Leitfähigkeit 1m (%)",
        help_text=(
            "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine "
            "Tiefe von einem Meter. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante "
            "angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten."
        )
    )
    hydraulic_conductivity_2m = forms.IntegerField(
        min_value=0,
        max_value=100,
        # initial=33,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_hydraulic_conductivity_2m",
            "name": "weighting_forest_hydraulic_conductivity_2m",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydraulische Leitfähigkeit 2m (%)",
        help_text=(
            "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine "
            "Tiefe von zwei Metern. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante "
            "angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten."
        )
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'forest-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'forest-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'))


class WeightingsAgricultureForm(forms.Form):
    field_capacity = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_field_capacity",
            "name": "weighting_agriculture_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Feldkapazität (%)",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydromorphy = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_hydromorphy",
            "name": "weighting_agriculture_hydromorphy",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydromorphie (%)",
        help_text = (
            "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen "
            "Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen."
        )
    )
    soil_type = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_soil_type",
            "name": "weighting_agriculture_soil_type",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Bodenart (%)",
        help_text = (
            "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." 
        )
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'agriculture-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button('agriculture-weighting-reset', 'Reset', css_class='btn-secondary reset-all'))
        

class WeightingsGrasslandForm(forms.Form):
    field_capacity = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_field_capacity",
            "name": "weighting_grassland_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Feldkapazität (%)",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydromorphy = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_hydromorphy",
            "name": "weighting_grassland_hydromorphy",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Hydromorphie (%)",
        help_text = (
            "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen "
            "Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen."
        )
    )
    soil_type = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_soil_type",
            "name": "weighting_grassland_soil_type",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Bodenart (%)",
        help_text = (
            "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." 
        )
    )
    soil_water_ratio = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_soil_water_ratio",
            "name": "weighting_grassland_soil_water_ratio",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Bodenfeuchte (%)",
        help_text= (
            "Bewertung der Sättigungsgrade von Böden auf Graslandstandorten."
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'grassland-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'

        self.helper.add_input(Button('grassland-weighting-reset', 'Reset', css_class='btn-secondary reset-all'))
        
class MarWeightingForm(forms.ModelForm):
    class Meta:
        model = models.MarWeighting
        fields = '__all__'

        labels = {
            'aquifer_thickness': "Mächtigkeit des Grundwasserleiters",
            'depth_groundwater': "Tiefe zum Grundwasserleiter 2",
            'hydraulic_conductivity': "Hydraulische Leitfähigkeit",
            'land_use': "Nutzung des Bodens",
            'distance_to_source_water': "Entfernung zum Rohwasser",
            'distance_to_well': "Entfernung zum Brunnen",
        }

        help_texts = {
            'aquifer_thickness': "Gewichtung der Mächtigkeit des Grundwasserleiters",
            'depth_groundwater': "Gewichtung der Tiefe zum Grundwasserleiter 2",
            'hydraulic_conductivity': "Gewichtung der hydraulischen Leitfähigkeit",
            'land_use': "Gewichtung der Landnutzung",
            'distance_to_source_water': "Gewichtung der Entfernung zum Rohwasser",
            'distance_to_well': "Gewichtung der Entfernung zum Brunnen (m)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default slider attributes
        default_attrs = {
            "data_range_min": 0,
            "data_range_max": 5,
            "string_label": True,
            "reset": True,
            "class": "hiddeninput",
        }

        # Apply the custom slider widget to all fields in the model
        for name, field in self.fields.items():
            attrs = default_attrs.copy()
            model_field = self._meta.model._meta.get_field(name)
            if model_field.default is not NOT_PROVIDED:
                attrs["data_cur_val"] = model_field.default
                attrs["data_default_value"] = model_field.default
            attrs["id"] = f"id_weighting_{name}"
            attrs["name"] = f"weighting_{name}"
            field.widget = CustomSimpleSliderWidget(attrs=attrs)

        # Crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'mar-weighting-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'mar-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'
        ))




class SuitabilityForm(forms.Form):
    def __init__(self, suitability, language='de', *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = models.MapLabels.objects.filter(suitability=suitability).order_by("order_position")
        default_attrs = {
            "data_range_min": 0,
            "data_range_max": 5,
            "string_label": True,
            "reset": True,
            "class": "hiddeninput",
        }
        for label in labels:
            # Pre-fill with default or existing project score  
            attrs = default_attrs.copy()
            
            attrs["data_cur_val"] = label.default_score
            attrs["data_default_value"] = label.default_score
            attrs["id"] = f"id_{suitability}_{label.name}"
            attrs["name"] = f"{suitability}_{label.name}"
            label_field = f"label_{language}"
            label_text = getattr(label, label_field, label.name)

            self.fields[label.name] = forms.IntegerField(
                widget=CustomSimpleSliderWidget(attrs=attrs),
                label=label_text,
            )

        # Crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = f'{suitability}-suitability-form'
        self.helper.form_class = 'form-horizontal suitability-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            f'{suitability}-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'
        ))
