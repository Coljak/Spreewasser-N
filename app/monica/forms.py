from . import models

from attr import attr
from django import forms

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions



class CropForm(forms.ModelForm):
    
    species = forms.ModelChoiceField(queryset=models.SpeciesParameters.objects.values_list('species_name', flat=True).distinct())

    class Meta:
        model = models.SpeciesParameters  # Assuming Crop is the model associated with the CropForm
        fields = ['species_name', 'species']  # Include species_name field in the form
