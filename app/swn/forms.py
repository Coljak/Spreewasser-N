
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import User, Crop, UserProject
from django.core import  validators


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('name', 'email', 'password')


class FormCrops(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name']
        widgets = {
            'name': forms.Select(attrs ={
                'class': 'form-control',
            }),
        }

# class UserProjectForm(forms.ModelForm):
#     class Meta:
#         model = UserProject
#         fields = [
#             'field.name',
#             'irrigation.date',
#             'irrigation.amount',
#             'comment'
#         ]
class UserProjectForm(forms.ModelForm):
    class Meta:
        model = UserProject
        fields = ['name', 'field', 'comment']
        widgets = {
            'name': forms.TextInput(),
            
        }
