
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



# class LoginForm(forms.ModelForm):

#     class Meta:
#         model = User
#         widgets = {
#             'password': forms.PasswordInput(),
#             }
#         fields = ('username', 'email', 'password')

class CropForm(forms.ModelForm):
    Feldfrucht = forms.ModelChoiceField(queryset=Crop.objects.all())

    class Meta:
        model = Crop
        fields = ['Feldfrucht']

# class CropForm(forms.ModelForm):
#     class Meta:
#         model = Crop
#         fields = ['name']
#         widgets = {
#             'name': forms.Select(attrs={
#                 'class': 'form-control',
#             }),
#         }


class UserProjectForm(forms.ModelForm):
    crop_id = forms.ModelChoiceField(queryset=Crop.objects.all())
    field_id =  forms.ModelChoiceField(queryset=UserField.objects.all())
    class Meta:
        model = UserProject
        
        fields = [
            'crop_id',
            # 'irrigation_input',
            # 'irrigation_output',
            'field_id',
            #'date',
            'comment',
            
        ]
        widgets = {
            'field_id.name': forms.Select(attrs={
                'class': 'form-control',
            }),
            'crop_id.name': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class UserFieldForm(forms.ModelForm):
    class Meta:
        model = UserField
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'id': 'fieldNameInput'}),
        }


# Selection of state, county and district

from .models import NUTS5000_N1, NUTS5000_N2, NUTS5000_N3

class PolygonSelectionForm(forms.Form):
    state_choices = sorted([(state.id, state.nuts_name) for state in NUTS5000_N1.objects.all()], key=lambda x: x[1])
    district_choices = sorted([(district.id, district.nuts_name) for district in NUTS5000_N2.objects.all()], key=lambda x: x[1])
    county_choices = sorted([(county.id, county.nuts_name) for county in NUTS5000_N3.objects.all()], key=lambda x: x[1])

    states = forms.MultipleChoiceField(
        # queryset= NUTS5000_N1.objects,
        choices=state_choices,
        widget=forms.SelectMultiple(attrs={'id': 'stateSelect', 'class': 'state-dropdown administrative-area'}),
        label=False,
        required=False,
    )
    
    districts = forms.MultipleChoiceField(
        # queryset= NUTS5000_N2.objects,
        choices=district_choices,
        widget=forms.SelectMultiple(attrs={'id': 'districtSelect', 'class': 'district-dropdown administrative-area'}),
        label=False,
        required=False,
    )
    counties = forms.MultipleChoiceField(
        # queryset= NUTS5000_N3.objects,
        choices=county_choices,
        widget=forms.SelectMultiple(attrs={'id': 'countySelect', 'class': 'county-dropdown administrative-area'}),
        label=False,
        required=False,
    )

    selected_states = forms.CharField(widget=forms.HiddenInput, required=False)
    selected_counties = forms.CharField(widget=forms.HiddenInput, required=False)
    selected_districts = forms.CharField(widget=forms.HiddenInput, required=False)

    # def __init__(self, *args, **kwargs):
    #     super(PolygonSelectionForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'list-group-item'
    # crispy helper
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_method = "POST"