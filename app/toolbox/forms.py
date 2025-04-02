from django import forms
from django.contrib.auth.models import User
from django.db.models import Max, Min
from .models import *
from django.db.models import Q
from toolbox.models import * #, SinksWithLandUseAndSoilProperties
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth.forms import UserCreationForm
from django.contrib.gis.geos import GEOSGeometry

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


# class SinksFilterForm(forms.Form):
#     depth_sink_min = forms.FloatField(required=False, label="Min Depth Sink")
#     depth_sink_max = forms.FloatField(required=False, label="Max Depth Sink")
#     area_sink_min = forms.FloatField(required=False, label="Min Area Sink")
#     area_sink_max = forms.FloatField(required=False, label="Max Area Sink")
#     volume_min = forms.FloatField(required=False, label="Min Volume")
#     volume_max = forms.FloatField(required=False, label="Max Volume")
    
#     land_use = forms.MultipleChoiceField(
#         widget=forms.CheckboxSelectMultiple, 
#         required=False, 
#         label="Land Use"
#     )

#     def __init__(self, *args, sink_extremes=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         print('sink_extremes',sink_extremes)
#         if sink_extremes:
#             self.fields['depth_sink_min'].min_value = sink_extremes['depth_sink_min']
#             self.fields['depth_sink_min'].max_value = sink_extremes['depth_sink_max']
#             self.fields['depth_sink_min'].initial = sink_extremes['depth_sink_min']

#             self.fields['depth_sink_max'].min_value = sink_extremes['depth_sink_min']
#             self.fields['depth_sink_max'].max_value = sink_extremes['depth_sink_max']
#             self.fields['depth_sink_max'].initial = sink_extremes['depth_sink_max']

#             self.fields['area_sink_min'].min_value = sink_extremes['area_sink_min']
#             self.fields['area_sink_min'].max_value = sink_extremes['area_sink_max']
#             self.fields['area_sink_min'].initial = sink_extremes['area_sink_min']

#             self.fields['area_sink_max'].min_value = sink_extremes['area_sink_min']
#             self.fields['area_sink_max'].max_value = sink_extremes['area_sink_max']
#             self.fields['area_sink_max'].initial = sink_extremes['area_sink_max']

#             self.fields['volume_min'].min_value = sink_extremes['volume_min']
#             self.fields['volume_min'].max_value = sink_extremes['volume_max']
#             self.fields['volume_min'].initial = sink_extremes['volume_min']

#             self.fields['volume_max'].min_value = sink_extremes['volume_min']
#             self.fields['volume_min'].max_value = sink_extremes['volume_max']
#             self.fields['volume_max'].initial = sink_extremes['volume_max']

#         # Define land use options dynamically
#         land_use_options = [
#             ('forest_deciduous_trees', 'Forest Deciduous Trees'),
#             ('heath', 'Heath'),
#             ('orchard_meadow', 'Orchard Meadow'),
#             ('vegetation', 'Vegetation'),
#             ('grassland', 'Grassland'),
#             ('agricultural_area_without_information', 'Agricultural Area Without Information'),
#             ('farmland', 'Farmland'),
#             ('woody_area', 'Woody Area'),
#             ('forest_conifers', 'Forest Conifers'),
#             ('forest_conifers_and_deciduous_trees', 'Forest Conifers and Deciduous Trees')
#         ]
#         self.fields['land_use'].choices = land_use_options
#         self.fields['land_use'].initial = [choice[0] for choice in land_use_options]  # Select all by default


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

    def __init__(self, *args, sink_extremes=None, **kwargs):
        super().__init__(*args, **kwargs)
        print('sink_extremes', sink_extremes)

        if sink_extremes:
            # Explicitly set min, max, and initial values inside the widget attributes
            self.fields['depth_sink_min'].widget.attrs.update({
                'min': sink_extremes['depth_sink_min'],
                'max': sink_extremes['depth_sink_max'],
                'value': sink_extremes['depth_sink_min'],
                'step': 0.05
            })

            self.fields['depth_sink_max'].widget.attrs.update({
                'min': sink_extremes['depth_sink_min'],
                'max': sink_extremes['depth_sink_max'],
                'value': sink_extremes['depth_sink_max'], 
                'step': 0.05
            })

            self.fields['area_sink_min'].widget.attrs.update({
                'min': sink_extremes['area_sink_min'],
                'max': sink_extremes['area_sink_max'],
                'value': sink_extremes['area_sink_min'],
                'step': 10
            })

            self.fields['area_sink_max'].widget.attrs.update({
                'min': sink_extremes['area_sink_min'],
                'max': sink_extremes['area_sink_max'],
                'value': sink_extremes['area_sink_max'],
                'step': 10
            })

            self.fields['volume_min'].widget.attrs.update({
                'min': sink_extremes['volume_min'],
                'max': sink_extremes['volume_max'],
                'value': sink_extremes['volume_min'],
                'step': 100
            })

            self.fields['volume_max'].widget.attrs.update({
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
