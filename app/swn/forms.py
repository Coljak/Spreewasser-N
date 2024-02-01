
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import Crop, UserProject, UserField, NUTS5000_N1, NUTS5000_N2, NUTS5000_N3, BuekSoilProfile, BuekPolygon, BuekSoilProfileHorizon
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


class CropForm(forms.ModelForm):
    Feldfrucht = forms.ModelChoiceField(queryset=Crop.objects.all())

    class Meta:
        model = Crop
        fields = ['Feldfrucht']


class UserProjectForm(forms.ModelForm):
    crop_id = forms.ModelChoiceField(queryset=Crop.objects.all())
    field_id =  forms.ModelChoiceField(queryset=UserField.objects.all())
    class Meta:
        model = UserProject
        
        fields = [
            'crop_id',
            'irrigation_input',
            'irrigation_output',
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
        # data = {}
        # for polygon_id in soil_profile_polygon_ids['buek_polygon_ids']:
        #     soil_data = BuekSoilProfileHorizon.objects.select_related('bueksoilprofile').filter(
        #         bueksoilprofile__polygon_id=polygon_id
        #         ).order_by('-bueksoilprofile__area_percenteage', 'bueksoilprofile__id', 'horizont_nr')
            
        #     for entry in soil_data:
        #         bueksoilprofile = entry.bueksoilprofile
        #         bueksoilprofile_id = bueksoilprofile.id
        #         landusage_id = bueksoilprofile.landusage

        #         # Create land usage entry if it doesn't exist
        #         if landusage_id not in data:
        #             data[landusage_id] = {'landusage_id': landusage_id, 'soil_profiles': {}}

        #         # Create soil profile entry if it doesn't exist
        #         if bueksoilprofile_id not in data[landusage_id]['soil_profiles']:
        #             data[landusage_id]['soil_profiles'][bueksoilprofile_id] = {
        #                 'system_unit': bueksoilprofile.system_unit,
        #                 'area_percenteage': bueksoilprofile.area_percenteage,
        #                 'horizons': {}
        #             }

        #         # Add horizon data to the respective soil profile
        #         horizon_nr = entry.horizont_nr
        #         data[landusage_id]['soil_profiles'][bueksoilprofile_id]['horizons'][horizon_nr] = {
        #             'obergrenze_m': entry.obergrenze_m,
        #             'untergrenze_m': entry.untergrenze_m,
        #             'stratigraphie': entry.stratigraphie,
        #             'herkunft': entry.herkunft,
        #             'geogenese': entry.geogenese,
        #             'fraktion': entry.fraktion,
        #             'summe': entry.summe,
        #             'gefuege': entry.gefuege,
        #             'torfarten': entry.torfarten,
        #             'substanzvolumen': entry.substanzvolumen,
        #             'bulk_density_class_id': entry.bulk_density_class_id,
        #             'humus_class_id': entry.humus_class_id,
        #             'ph_class_id': entry.ph_class_id
        #         }

        