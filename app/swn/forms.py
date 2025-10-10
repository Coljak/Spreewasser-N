
from attr import attr
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User

from . import models
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
        model = models.UserField
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
            (instance.id, instance.name) for instance in models.SwnProject.objects.filter(Q(user=user))
        ]
        self.helper = monica_forms.get_row_form_helper()
        self.helper.layout = Layout(
            Field('monica_project', wrapper_class='row')
            
        )

# Selection of state, county and district


# Todo make this a ModelForm, model = NUTS5000_N3 ?
class PolygonSelectionForm(forms.Form):
    states = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'id': 'stateSelect', 'class': 'state-dropdown administrative-area'}),
        label=False,
        required=False,
    )
    districts = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'id': 'districtSelect', 'class': 'district-dropdown administrative-area'}),
        label=False,
        required=False,
    )
    counties = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'id': 'countySelect', 'class': 'county-dropdown administrative-area'}),
        label=False,
        required=False,
    )

    selected_states = forms.CharField(widget=forms.HiddenInput, required=False)
    selected_counties = forms.CharField(widget=forms.HiddenInput, required=False)
    selected_districts = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['states'].choices = sorted(
                [(s.id, s.nuts_name) for s in models.NUTS5000_N1.objects.all()],
                key=lambda x: x[1]
            )
            self.fields['districts'].choices = sorted(
                [(d.id, d.nuts_name) for d in models.NUTS5000_N2.objects.all()],
                key=lambda x: x[1]
            )
            self.fields['counties'].choices = sorted(
                [(c.id, c.nuts_name) for c in models.NUTS5000_N3.objects.all()],
                key=lambda x: x[1]
            )
        except Exception as e:
            # When DB is not ready (e.g. migrations), silently skip
            print(f"PolygonSelectionForm init skipped: {e}")




# class SwnNewProjectForm(monica_forms.MonicaNewProjectForm):
#     user_field = forms.ModelChoiceField(
#         queryset=models.UserField.objects.all(),
#         label='Field',
#         widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
#     )
#     def __init__(self, *args, user=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         if user is not None:
#             self.fields['user_field'].choices = [
#                 (instance.id, instance.name) for instance in models.UserField.objects.filter(Q(user=user)).order_by('name')
#             ]
#             monica_projects = MonicaProject.objects.filter(Q(user=user))
#             mp = [( monica_project.monica_model_setup.id, monica_project.name) for monica_project in monica_projects]
#             default_setup = ModelSetup.objects.filter(is_default=True)[0]
#             setup_choices = [(default_setup.id, default_setup.name)] + mp
#             print(setup_choices, mp)

#             self.fields['monica_model_setup'].choices = setup_choices

class SwnNewProjectForm(monica_forms.MonicaNewProjectForm):
    user_field = forms.ModelChoiceField(
        queryset=models.UserField.objects.none(),
        label='Field',
        widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, user=user, **kwargs)

        if user is not None:
            self.fields['user_field'].queryset = models.UserField.objects.filter(user=user).order_by('name')

            # Set up monica_model_setup choices
            monica_projects = MonicaProject.objects.filter(user=user)
            mp = [(mp.monica_model_setup.id, mp.name) for mp in monica_projects]
            default_setup = ModelSetup.objects.filter(is_default=True).first()
            setup_choices = [(default_setup.id, default_setup.name)] + mp
            self.fields['monica_model_setup'].choices = setup_choices

            self.helper.layout.fields.insert(0, Field('user_field', wrapper_class='row'))

        # # ✅ Update the Crispy layout to include the new field
        # # If the parent class already has a helper, extend it
        # if hasattr(self, 'helper') and self.helper is not None:
        #     # insert user_field at the top of the layout
        #     self.helper.layout.fields.insert(0, Field('user_field', wrapper_class='row'))
        # else:
        #     # define a new helper if parent didn't create one
        #     self.helper = get_row_form_helper()
        #     self.helper.layout = Layout(
        #         Field('user_field', wrapper_class='row'),
        #         Field('name', wrapper_class='row'),
        #         Field('description', wrapper_class='row'),
        #         Field('start_date', wrapper_class='row'),
        #         Field('monica_model_setup', wrapper_class='row'),
            # )



# class SwnNewProjectForm(forms.Form):
#     text = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
#         label='User text',
#         required=False
#     )

#     def __init__(self, *args, user=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         if user is not None:
#             # Set initial value for the textarea
#             self.fields['text'].initial = getattr(user, 'username', str(user))



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


       