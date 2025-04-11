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

from .widgets import CustomRangeSliderWidget, CustomSingleSliderWidget

class SingleWidgetForm(forms.Form):
    distance_to_userfield = forms.FloatField(
        required=False,
        label="Distance to userfield (m)",
        widget=CustomSingleSliderWidget()
    )

class DoubleWidgetForm(forms.Form):
    double_slider = forms.FloatField(
        required=False,
        label="Distance to userfield (m)",
        widget=CustomRangeSliderWidget()
    )

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
                layout_fields.append(layout_field)
            elif field_name == "distance_to_userfield":
                layout_fields.append(Field(field_name, template="forms/fields/single-slider.html"))

            else:
                layout_field = Field(field_name)
                layout_fields.append(layout_field)
        self.helper.layout = Layout(*layout_fields)

        for f in self.fields:
            print(f)
            if f == 'land_use':
                self.fields['land_use'].initial = [
                    choice[0] for choice in self.fields['land_use'].choices
                ]
                print('land_use field found', self.fields['land_use'].initial)


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
