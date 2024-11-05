from django import forms
from django.contrib.auth.models import User
from django.db.models import Max, Min

from toolbox.models import UserProject, SinksWithLandUseAndSoilProperties
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth.forms import UserCreationForm

SINK_EXTREMES = SinksWithLandUseAndSoilProperties.objects.aggregate(
    depth_sink_min=Min('depth_sink'),
    depth_sink_max=Max('depth_sink'),
    area_sink_min=Min('area_sink'),
    area_sink_max=Max('area_sink'),
)

class UserProjectForm(forms.ModelForm):
    class Meta:
        model = UserProject
        fields = [
            'name',
            'description',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

class SinksFilterForm(forms.Form):
    depth_sink_min = forms.FloatField(required=False, label="Min Depth Sink", min_value=SINK_EXTREMES['depth_sink_min'], max_value=SINK_EXTREMES['depth_sink_max'], initial=SINK_EXTREMES['depth_sink_min'])
    depth_sink_max = forms.FloatField(required=False, label="Max Depth Sink",  min_value=SINK_EXTREMES['depth_sink_min'], max_value=SINK_EXTREMES['depth_sink_max'], initial=SINK_EXTREMES['depth_sink_max'])
    area_sink_min = forms.FloatField(required=False, label="Min Area Sink",  min_value=SINK_EXTREMES['area_sink_min'], max_value=SINK_EXTREMES['area_sink_max'], initial=SINK_EXTREMES['area_sink_min'])
    area_sink_max = forms.FloatField(required=False, label="Max Area Sink",  min_value=SINK_EXTREMES['area_sink_min'], max_value=SINK_EXTREMES['area_sink_max'], initial=SINK_EXTREMES['area_sink_max'])
    
    # This field is a calculated field (area_sink * depth_sink)
    volume_min = forms.FloatField(required=False, label="Min Volume",  min_value=0, initial=SINK_EXTREMES['area_sink_min'] * SINK_EXTREMES['depth_sink_min'])
    volume_max = forms.FloatField(required=False, label="Max Volume",  min_value=0, initial=SINK_EXTREMES['area_sink_max'] * SINK_EXTREMES['depth_sink_max'])

    # Dynamic radio buttons for land use selection (values greater than 0)
    land_use = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False, label="Land Use" )

    def __init__(self, *args, **kwargs):
        super(SinksFilterForm, self).__init__(*args, **kwargs)
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
        # Set all checkboxes to selected by default
        self.fields['land_use'].initial = [choice[0] for choice in land_use_options]