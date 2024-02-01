from django import forms
from django.contrib.auth.models import User

from toolbox.models import UserProject
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth.forms import UserCreationForm

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