
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

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user','')
#         super(UserProjectForm, self).__init__(*args, **kwargs)
        #self.fields['user_defined_code']=forms.ModelChoiceField(queryset=UserDefinedCode.objects.filter(owner=user))


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

