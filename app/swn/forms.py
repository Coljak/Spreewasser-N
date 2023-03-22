
from attr import attr
from django import forms
from django.contrib.auth.models import User

from swn.models import User, Crop, UserProject, UserField#, UserInfo
from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


# class UserInfoForm(forms.ModelForm):
#     class Meta():
#         model = UserInfo
#         fields = ('name', 'email', 'password')
    
    

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    # helper.layout = Layout(
    #     Field('text_input', css_class='input-xlarge'),
    #     Field('textarea', rows="3", css_class='input-xlarge'),
    #     'radio_buttons',
    #     Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
    #     AppendedText('appended_text', '.00'),
    #     PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">', active=True),
    #     PrependedText('prepended_text_two', '@'),
    #     'multicolon_select',
    #     FormActions(
    #         Submit('save_changes', 'Save changes', css_class="btn-primary"),
    #         Submit('cancel', 'Cancel'),
    #     )

    class Meta():
        model = User
        fields = ('name', 'email', 'password')


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
