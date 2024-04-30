from . import models

from attr import attr
from django import forms

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from .models import SpeciesParameters, CultivarParameters

class CultivarParametersForm(forms.Form):
    species_parameters = forms.ModelChoiceField(queryset=SpeciesParameters.objects.all(), empty_label="Select Species")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cultivar_parameters'] = forms.ModelChoiceField(queryset=CultivarParameters.objects.none(), empty_label="Select Cultivar")

