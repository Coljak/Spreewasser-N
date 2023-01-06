
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import User, Crop
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


class FormSidebar(forms.Form):
    name = forms.CharField(label='label')
    email = forms.EmailField()
    text = forms.CharField(widget=forms.Textarea)
    botcatcher = forms.CharField(required=False,
                        widget=forms.HiddenInput,
                        validators=[validators.MaxLengthValidator(0)]
        )
                             
    #TODO not working

    def clean_botcather(self):
        botcatcher = self.cleaned_data['botcatcher']
        if len(botcatcher) > 0:
            raise (forms.ValidationError("GOTCHA BOT!"))
        return botcatcher