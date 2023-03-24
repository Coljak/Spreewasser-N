
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import Crop, UserProject, UserField  # , UserInfo
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# class UserForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ('name', 'email', 'password1', 'password2')

# class LoginForm(forms.ModelForm):
    
#     class Meta:
#         model = User
#         widgets = {
#             'password': forms.PasswordInput(),
#             }
#         fields = ('username', 'email', 'password')


class FormCrops(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name']
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

# class UserProjectForm(forms.ModelForm):
#     class Meta:
#         model = UserProject

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user','')
#         super(UserProjectForm, self).__init__(*args, **kwargs)
        # self.fields['user_defined_code']=forms.ModelChoiceField(queryset=UserDefinedCode.objects.filter(owner=user))

        # fields = [
        #     'user_field.name',
        #     'comment',
        #     'crop.name'
        # ]
        # widgets = {
        #     'field.name': forms.Select(attrs ={
        #         'class': 'form-control',
        #     }),
        #     'crop.name': forms.Select(attrs ={
        #         'class': 'form-control',
        #     }),
        # }


class UserFieldForm(forms.ModelForm):
    class Meta:
        model = UserField
        fields = ('name',)
