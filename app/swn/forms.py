
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import UserProject, UserField, NUTS5000_N1, NUTS5000_N2, NUTS5000_N3
from buek.models import SoilProfile, BuekPolygon, SoilProfileHorizon
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






class UserFieldForm(forms.ModelForm):
    class Meta:
        model = UserField
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'id': 'fieldNameInput'}),
        }


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


class SoilProfileSelectionForm(forms.Form):
    land_usage = forms.ChoiceField(label='Land Usage', choices=[])
    area_percenteage = forms.ChoiceField(label='Area Percentage', choices=[])
    system_unit = forms.ChoiceField(label='System Unit', choices=[])
    soil_profile = forms.ChoiceField(label='Soil Profile', choices=[])
    horizons = forms.CharField(label='Horizons', widget=forms.Textarea, required=False)
       
    # choices for land usage are set here, all other choices are set in the front end
    def set_choices(self, choices_data):
       self.fields['land_usage'].choices = choices_data
       