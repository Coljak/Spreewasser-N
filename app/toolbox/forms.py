from django import forms
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Max, Min
from .models import *
from django.db.models import Q
from toolbox.models import * #, SinksWithLandUseAndSoilProperties
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, StrictButton
from django_filters.fields import RangeField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.gis.geos import GEOSGeometry





class SliderFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
    # def __init__(self, *args, model=None, form_action=None, **kwargs):
        super().__init__(*args,  **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        # self.helper.form_class = 'form-horizontal'
        self.helper.form_id = 'sink-filter-form'
        
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2 col-md-2 col-sm-auto'
        self.helper.field_class = 'col-lg-10 col-md-10 col-sm-auto'

        layout_fields = []
        for field_name, field in self.fields.items():
            if isinstance(field, RangeField):
                layout_field = Field(field_name, template="forms/fields/range-slider.html")
            else:
                layout_field = Field(field_name)
            layout_fields.append(layout_field)
        # layout_fields.append(StrictButton("Filter sinks", name='filter_sinks', type='submit', css_class='btn btn-fill-out btn-block mt-1'))
        self.helper.layout = Layout(*layout_fields)







SINK_EXTREMES = Sink.objects.aggregate(
    depth_sink_min=Min('depth'),
    depth_sink_max=Max('depth'),
    area_sink_min=Min('area'),
    area_sink_max=Max('area'),
)

ENLARGED_SINK_EXTREMES = EnlargedSink.objects.aggregate(
    depth_sink_min=Min('depth'),
    depth_sink_max=Max('depth'),
    area_sink_min=Min('area'),
    area_sink_max=Max('area'),
)


class SinksFilterForm(forms.Form):
    depth_sink_min = forms.FloatField(required=False, label="Min Depth Sink")
    depth_sink_max = forms.FloatField(required=False, label="Max Depth Sink")
    area_sink_min = forms.FloatField(required=False, label="Min Area Sink")
    area_sink_max = forms.FloatField(required=False, label="Max Area Sink")
    volume_min = forms.FloatField(required=False, label="Min Volume")
    volume_max = forms.FloatField(required=False, label="Max Volume")
    
    land_use = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, 
        required=False, 
        label="Land Use"
    )

    def __init__(self, *args, sink_extremes=None, enlarged_sinks=False, **kwargs):
        super().__init__(*args, **kwargs)

        id_suffix = "_enlarged" if enlarged_sinks else ""

        if sink_extremes:
            self.fields['depth_sink_min'].widget.attrs.update({
                'id': f"id_depth_sink_min{id_suffix}",
                'min': sink_extremes['depth_sink_min'],
                'max': sink_extremes['depth_sink_max'],
                'value': sink_extremes['depth_sink_min'],
                'step': 0.05
            })

            self.fields['depth_sink_max'].widget.attrs.update({
                'id': f"id_depth_sink_max{id_suffix}",
                'min': sink_extremes['depth_sink_min'],
                'max': sink_extremes['depth_sink_max'],
                'value': sink_extremes['depth_sink_max'], 
                'step': 0.05
            })

            self.fields['area_sink_min'].widget.attrs.update({
                'id': f"id_area_sink_min{id_suffix}",
                'min': sink_extremes['area_sink_min'],
                'max': sink_extremes['area_sink_max'],
                'value': sink_extremes['area_sink_min'],
                'step': 10
            })

            self.fields['area_sink_max'].widget.attrs.update({
                'id': f"id_area_sink_max{id_suffix}",
                'min': sink_extremes['area_sink_min'],
                'max': sink_extremes['area_sink_max'],
                'value': sink_extremes['area_sink_max'],
                'step': 10
            })

            self.fields['volume_min'].widget.attrs.update({
                'id': f"id_volume_min{id_suffix}",
                'min': sink_extremes['volume_min'],
                'max': sink_extremes['volume_max'],
                'value': sink_extremes['volume_min'],
                'step': 100
            })

            self.fields['volume_max'].widget.attrs.update({
                'id': f"id_volume_max{id_suffix}",
                'min': sink_extremes['volume_min'],
                'max': sink_extremes['volume_max'],
                'value': sink_extremes['volume_max'],
                'step': 100
            })

        # Define land use options dynamically
        land_use_options = [
            ('forest_deciduous_trees', 'Forest Deciduous Trees'),
            ('heath', 'Heath'),
            ('orchard_meadow', 'Orchard Meadow'),
            ('vegetation', 'Vegetation'),
            ('grassland', 'Grassland'),
            ('agricultural_area_without_information', 'Agricultural Area Without Information'),
            ('farmland', 'Farmland'),
            ('woody_area', 'Woody Area'),
            ('forest_conifers', 'Forest Conifers'),
            ('forest_conifers_and_deciduous_trees', 'Forest Conifers and Deciduous Trees')
        ]
        
        self.fields['land_use'].choices = land_use_options
        self.fields['land_use'].initial = [choice[0] for choice in land_use_options]  # Select all by default


class WaterbodyFilterForm(forms.Form):
    min_min_surplus_volume = forms.FloatField(
        required=False, 
        label="Minimum Überschussvolumen Untergrenze"
    )
    max_min_surplus_volume = forms.FloatField(
        required=False, 
        label="Minimum Überschussvolumen Obergrenze"
    )
    min_max_surplus_volume = forms.FloatField(
        required=False, 
        label="Maximum Überschussvolumen Untergrenze"
    )
    max_max_surplus_volume = forms.FloatField(
        required=False, 
        label="Maximum Überschussvolumen Obergrenze"
    )
    min_mean_surplus_volume = forms.FloatField(
        required=False, 
        label="Durchnittliches Überschussvolumen Untergrenze"
    )
    max_mean_surplus_volume = forms.FloatField(
        required=False, 
        label="Durchnittliches Überschussvolumen Obergrenze"
    )
    min_plus_days = forms.FloatField(
        required=False, 
        label="Überschusstage Untergrenze"
    )
    max_plus_days = forms.FloatField(
        required=False, 
        label="Überschusstage Obergrenze"
    )

    def __init__(self, *args, extremes=None, lake=False, **kwargs):
        super().__init__(*args, **kwargs)

        id_suffix = "_lake" if lake else "_stream"

        if extremes:
            self.fields['min_min_surplus_volume'].widget.attrs.update({
                'id': f"id_min_min_surplus_volume{id_suffix}",
                'type':"range",
                'class': "form-range",
                'min': extremes['min_min_surplus_volume'],
                'max': extremes['max_min_surplus_volume'],
                'value': extremes['min_min_surplus_volume'],
                'step': 0.05
            })

            self.fields['max_min_surplus_volume'].widget.attrs.update({
                'id': f"id_max_min_surplus_volume{id_suffix}",
                'min': extremes['min_min_surplus_volume'],
                'max': extremes['max_min_surplus_volume'],
                'value': extremes['max_min_surplus_volume'],
                'step': 0.05
            })

            self.fields['min_mean_surplus_volume'].widget.attrs.update({
                'id': f"id_min_mean_surplus_volume{id_suffix}",
                'min': extremes['min_mean_surplus_volume'],
                'max': extremes['max_mean_surplus_volume'],
                'value': extremes['min_mean_surplus_volume'],
                'step': 0.05
            })

            self.fields['max_min_surplus_volume'].widget.attrs.update({
                'id': f"id_max_mean_surplus_volume{id_suffix}",
                'min': extremes['min_mean_surplus_volume'],
                'max': extremes['max_mean_surplus_volume'],
                'value': extremes['max_mean_surplus_volume'],
                'step': 0.05
            })

            self.fields['min_max_surplus_volume'].widget.attrs.update({
                'id': f"id_min_max_surplus_volume{id_suffix}",
                'min': extremes['min_max_surplus_volume'],
                'max': extremes['max_max_surplus_volume'],
                'value': extremes['min_max_surplus_volume'],
                'step': 0.05
            })

            self.fields['max_max_surplus_volume'].widget.attrs.update({
                'id': f"id_max_max_surplus_volume{id_suffix}",
                'min': extremes['min_max_surplus_volume'],
                'max': extremes['max_max_surplus_volume'],
                'value': extremes['max_max_surplus_volume'],
                'step': 0.05
            })


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
            (instance.id, instance.name) for instance in ToolboxProject.objects.filter(Q(user=user))
        ]

    


class ToolboxProjectForm(forms.Form):
    user_field = forms.ModelChoiceField(
        queryset=UserField.objects.all(),
        label='Field',
        widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
    )
    project_type = forms.ModelChoiceField(
        queryset = ToolboxType.objects.all(),
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
        model = ToolboxProject
        exclude = ['id', 'user']
