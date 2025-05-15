
from attr import attr
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User

from swn.models import *
from buek.models import SoilProfile, BuekPolygon, SoilProfileHorizon
from monica.models import MonicaProject, ModelSetup
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth.forms import UserCreationForm
from monica import forms as monica_forms


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']






class UserFieldForm(forms.ModelForm):
    class Meta:
        model = UserField
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'id': 'fieldNameInput'}),
        }



class SwnProjectSelectionForm(forms.Form):
    monica_project = forms.ChoiceField(
        choices=[],
        label="Swn Project",
        widget=forms.Select(attrs={'class': 'form-control monica-project'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monica_project'].choices = [
            (instance.id, instance.name) for instance in MonicaProject.objects.filter(Q(user=user))
        ]
        self.helper = monica_forms.get_row_form_helper()
        self.helper.layout = Layout(
            Field('monica_project', wrapper_class='row')
            
        )

# Selection of state, county and district


# Todo make this a ModelForm, model = NUTS5000_N3 ?
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



class SwnProjectForm(monica_forms.MonicaProjectForm):
    user_field = forms.ModelChoiceField(
        queryset=UserField.objects.all(),
        label='Field',
        widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
    )
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['user_field'].choices = [
                (instance.id, instance.name) for instance in UserField.objects.filter(Q(user=user)).order_by('name')
            ]
            monica_projects = MonicaProject.objects.filter(Q(user=user))
            mp = [( monica_project.monica_model_setup.id, monica_project.name) for monica_project in monica_projects]
            default_setup = ModelSetup.objects.filter(is_default=True)[0]
            setup_choices = [(default_setup.id, default_setup.name)] + mp
            print(setup_choices, mp)

            self.fields['monica_model_setup'].choices = setup_choices


# TODO this is probably obsolete
class SoilProfileSelectionForm(forms.Form):
    land_usage = forms.ChoiceField(label='Land Usage', choices=[])
    area_percentage = forms.ChoiceField(label='Area Percentage', choices=[])
    system_unit = forms.ChoiceField(label='System Unit', choices=[])
    soil_profile = forms.ChoiceField(label='Soil Profile', choices=[])
    horizons = forms.CharField(label='Horizons', widget=forms.Textarea, required=False)
       
    # choices for land usage are set here, all other choices are set in the front end
    def set_choices(self, choices_data):
       self.fields['land_usage'].choices = choices_data


       