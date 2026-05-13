from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Column, Field



class InfoLabelFormMixin():
    # Helper method to add info icon to labels if a help_text exists
    def label_with_info(self, field_name):
        field = self.fields[field_name]
        if field.help_text:
            info_icon = f'<i class="bi bi-info-circle" data-help="{field.help_text}"></i>'
            field.help_text = ""   #  remove normal help_text output
            return mark_safe(f"{field.label} {info_icon}")
        return field.label

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.label = self.label_with_info(name)


class ResultForm(InfoLabelFormMixin, forms.Form):
    def __init__(self, *args, toolbox_type=None, **kwargs):  # fixed signature
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            field.widget.attrs.update({'prefix': 'result', 'name': key})
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = f'{toolbox_type}-result-download-form'
        self.helper.form_class = 'form-horizontal download-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(
            Submit(
                f'{toolbox_type}-results', 
                'Download', 
                css_class='btn-primary download-results', 
                **{'data-type': toolbox_type}
                )
                )



class CheckboxSelectMultipleWithAttrs(forms.CheckboxSelectMultiple):
    def __init__(self, attrs=None, choice_attrs=None):
        super().__init__(attrs)
        self.choice_attrs = choice_attrs or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if str(value) in self.choice_attrs:
            option['attrs'].update(self.choice_attrs[str(value)])
        return option
