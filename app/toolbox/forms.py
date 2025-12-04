from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.db.models import Max, Min, NOT_PROVIDED
from . import models
from swn import models as swn_models
# from swn import forms as swn_forms
# from .utils import widgets
from django.db.models import Q

from django.core import validators
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field


from utilities.widgets import CustomRangeSliderWidget, CustomSingleSliderWidget,CustomSimpleSliderWidget, CustomDoubleSliderWidget

class InfoLabelFormMixin():
    # Helper method to add info icon to labels if a help_text exists
    def label_with_info(self, field_name):
        field = self.fields[field_name]
        if field.help_text:
            info_icon = f'<i class="bi bi-info-circle" data-help="{field.help_text}"></i>'
            field.help_text = ""   # ⬅️ remove normal help_text output
            return mark_safe(f"{field.label} {info_icon}")
        return field.label

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.label = self.label_with_info(name)

class CheckboxSelectMultipleWithAttrs(forms.CheckboxSelectMultiple):
    def __init__(self, attrs=None, choice_attrs=None):
        super().__init__(attrs)
        self.choice_attrs = choice_attrs or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if str(value) in self.choice_attrs:
            option['attrs'].update(self.choice_attrs[str(value)])
        return option

  
class SliderFilterForm(InfoLabelFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2 col-md-2 col-sm-auto'
        self.helper.field_class = 'col-lg-10 col-md-10 col-sm-auto'

        self.helper.layout = Layout(*[Field(name) for name in self.fields])



### SIDEBAR #####
# toolbox/forms.py

# Todo make this a ModelForm, model = NUTS5000_N3 ?
class PolygonSelectionForm(forms.Form):

    counties = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'id': 'countiesSelect', 'class': 'county-dropdown administrative-area btn'}),
        label=False,
        required=False,
    )

    selected_counties = forms.CharField(widget=forms.HiddenInput, required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            pr = swn_models.ProjectRegion.objects.first()
            self.fields['counties'].choices = sorted(
                [(c.id, c.nuts_name) for c in swn_models.NUTS5000_N3.objects.filter(Q(geom__intersects=pr.geom) | Q(geom__within=pr.geom))],
                key=lambda x: x[1]
            )
        except Exception as e:
            # When DB is not ready (e.g. migrations), silently skip
            print(f"PolygonSelectionForm init skipped: {e}")




class ToolboxProjectSelectionForm(InfoLabelFormMixin, forms.Form):
    toolbox_project = forms.ChoiceField(
        required=False,
        choices=[],
        label="Projekt",
        widget=forms.Select(attrs={'class': 'form-control toolbox-project'})
    )

    def __init__(self, *args,qs=None, data_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if qs:
            self.fields['toolbox_project'].choices = [
                (instance.id, instance.name) for instance in qs
            ]

        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-horizontal toolbox-selection-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'load-project', 
            'Laden', 
            css_class='toolbox-load-project btn btn-secondary',
            **{'data-type': data_type}))
        self.helper.add_input(Button(
            'delete-project', 
            'Löschen', 
            css_class='toolbox-delete-project btn btn-secondary',
            **{'data-type': data_type}))
        self.helper.add_input(Button(
            'info-project', 
            'Projektinfo', 
            css_class='toolbox-project-info btn btn-secondary',
            **{'data-type': data_type}))
        self.helper.add_input(Button(
            'new-project', 
            'Neues Projekt', 
            css_class='toolbox-new-project btn btn-secondary',
            **{'data-type': data_type}))
        



class ToolboxProjectForm(InfoLabelFormMixin, forms.Form):
    user_field = forms.ModelChoiceField(
        # TODO this line should be deleted
        queryset=models.UserField.objects.all(),
        label='Suchgebiet',
        widget=forms.Select(attrs={'id': 'userFieldSelect', 'class': 'user-field-dropdown'}),
    )
    project_type = forms.ModelChoiceField(
        queryset = models.ToolboxType.objects.all(),
        label='Tool',
        empty_label=None,
        to_field_name='name_tag',
        widget=forms.Select(attrs={'id': 'projectTypeSelect', 'class': 'project-type-dropdown'}),
    )
    project_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_project_name', 'required': 'required',}),
        label='Project Name',
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_project_description'}),
        label='Description',
        required=False
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['user_field'].queryset = models.UserField.objects.filter(user=user)
        else:
            self.fields['user_field'].queryset = models.UserField.objects.none()

    class Meta:
        model = models.ToolboxProject
        exclude = ['id', 'user']


class InletWeightingsForm(InfoLabelFormMixin, forms.Form):
    weighting_inlet_length = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_inlet_length",
            "name": "weighting_inlet_length",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 70,
            "data_default_value": 70,
            "units": "%",
        }),
        label="Gewichtung der Länge der Zuleitung",
        help_text=(
            "Die Gewichtung der Länge der Zuleitung "
        )
    )

    weighting_inlet_volume = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_inlet_volume",
            "name": "weighting_inlet_volume",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 30,
            "data_default_value": 30,
            "units": "%",
        }),
        label="Gewichtung des Verhältnisses ökologischer Mindestabflusses zu Senkenvolumen",
        help_text=(
            "Gewichtung der ... "
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'overall-weighting-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'overall-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'))
class OverallWeightingsForm(InfoLabelFormMixin, forms.Form):
    overall_usability = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_overall_usability",
            "name": "weighting_overall_usability",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 20,
            "data_default_value": 20,
            "units": "%",
        }),
        label="Gewichtung des Untergrundspeichervolumens",
        help_text=(
            "Die allgemeine Nutzbarkeit ist eine Bewertung der Eignung des Standorts für "
            "Versickerungsmaßnahmen. Eine hohe Bewertung begünstigt Versickerungsmaßnahmen."
        )
    )

    soil_index = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_soil_index",
            "name": "weighting_soil_index",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 80,
            "data_default_value": 80,
            "units": "%",
        }),
        label="Gewichtung der Bodenbewertung",
        help_text=(
            "Gewichtung der Bodenbewertung ist eine Bewertung der Eignung des Standorts für "
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'overall-weighting-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'overall-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'))


      
class WeightingsForestForm(InfoLabelFormMixin, forms.Form):
    field_capacity = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_field_capacity",
            "name": "weighting_forest_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
            
        }),
        label="Feldkapazität",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydraulic_conductivity_1m = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        # initial=33,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_hydraulic_conductivity_1m",
            "name": "weighting_forest_hydraulic_conductivity_1m",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydraulische Leitfähigkeit 1m",
        help_text=(
            "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine "
            "Tiefe von einem Meter. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante "
            "angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten."
        )
    )
    hydraulic_conductivity_2m = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        # initial=33,
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_forest_hydraulic_conductivity_2m",
            "name": "weighting_forest_hydraulic_conductivity_2m",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydraulische Leitfähigkeit 2m",
        help_text=(
            "Die hydraulische Leitfähigkeit ist die gesättigte Wasserleitfähigkeit des Bodens bis in eine "
            "Tiefe von zwei Metern. Bei aktiver Nutzung werden gesättigte Bedingungen unterhalb der Geländeoberkante "
            "angenommen. Eine hohe Leitfähigkeit begünstigt hohe Versickerungsraten."
        )
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'forest-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'forest-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'))


class WeightingsAgricultureForm(InfoLabelFormMixin, forms.Form):
    field_capacity = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_field_capacity",
            "name": "weighting_agriculture_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Feldkapazität",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydromorphy = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_hydromorphy",
            "name": "weighting_agriculture_hydromorphy",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Hydromorphie",
        help_text = (
            "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen "
            "Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen."
        )
    )
    soil_type = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=33, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_agriculture_soil_type",
            "name": "weighting_agriculture_soil_type",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 33,
            "data_default_value": 33,
            "units": "%",
        }),
        label="Bodenart",
        help_text = (
            "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." 
        )
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'agriculture-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button('agriculture-weighting-reset', 'Reset', css_class='btn-secondary reset-all'))
        

class WeightingsGrasslandForm(InfoLabelFormMixin, forms.Form):
    field_capacity = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_field_capacity",
            "name": "weighting_grassland_field_capacity",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Feldkapazität",
        help_text = (
            "Die Feldkapazität ist das Wasservolumen das über längere Zeit entgegen der "
            "Schwerkraft im Boden gehalten werden kann. Eine geringere Feldkapazität begünstigt "
            "Versickerungsmaßnahmen."
        )
    )
    hydromorphy = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_hydromorphy",
            "name": "weighting_grassland_hydromorphy",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Hydromorphie",
        help_text = (
            "Die Hydromorphie unterscheidet zwischen grund-, stau- und sickerwasserdominierten landwirtschaftlichen "
            "Standorten. Für Versickerungsmaßnahmen sind letztere zu bevorzugen."
        )
    )
    soil_type = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_soil_type",
            "name": "weighting_grassland_soil_type",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Bodenart",
        help_text = (
            "Bewertung der Eignung der vorliegenden Bodenarten landwirtschaftlicher Standorte für Versickerungmaßnahmen." 
        )
    )
    soil_water_ratio = forms.IntegerField(
        required=False,
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_weighting_grassland_soil_water_ratio",
            "name": "weighting_grassland_soil_water_ratio",
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 25,
            "data_default_value": 25,
            "units": "%",
        }),
        label="Bodenfeuchte",
        help_text= (
            "Bewertung der Sättigungsgrade von Böden auf Graslandstandorten."
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'grassland-weighting-filter-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'

        self.helper.add_input(Button('grassland-weighting-reset', 'Reset', css_class='btn-secondary reset-all'))
        
class MarWeightingForm(InfoLabelFormMixin, forms.ModelForm):
    class Meta:
        model = models.MarWeighting
        fields = '__all__'

        labels = {
            'aquifer_thickness': "Mächtigkeit des Grundwasserleiters",
            'depth_groundwater': "Tiefe zum Grundwasserleiter 2",
            'hydraulic_conductivity': "Hydraulische Leitfähigkeit",
            'land_use': "Nutzung des Bodens",
            'distance_to_source_water': "Entfernung zum Rohwasser",
            'distance_to_well': "Entfernung zum Brunnen",
        }

        help_texts = {
            'aquifer_thickness': "Gewichtung der Mächtigkeit des Grundwasserleiters",
            'depth_groundwater': "Gewichtung der Tiefe zum Grundwasserleiter 2",
            'hydraulic_conductivity': "Gewichtung der hydraulischen Leitfähigkeit",
            'land_use': "Gewichtung der Landnutzung",
            'distance_to_source_water': "Gewichtung der Entfernung zum Rohwasser",
            'distance_to_well': "Gewichtung der Entfernung zum Brunnen (m)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default slider attributes
        default_attrs = {
            "data_range_min": 0,
            "data_range_max": 5,
            "string_label": True,
            "reset": True,
            "class": "hiddeninput",
        }

        # Apply the custom slider widget to all fields in the model
        for name, field in self.fields.items():
            field.required=False
            attrs = default_attrs.copy()
            model_field = self._meta.model._meta.get_field(name)
            # if model_field.default is not NOT_PROVIDED:
            attrs["data_cur_val"] = model_field.default
            attrs["data_default_value"] = model_field.default
            attrs["id"] = f"id_weighting_{name}"
            attrs["name"] = f"weighting_{name}"
            field.widget = CustomSimpleSliderWidget(attrs=attrs)

        # Crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'mar-weighting-form'
        self.helper.form_class = 'form-horizontal weighting-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            'mar-weighting-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'
        ))




class SuitabilityForm(InfoLabelFormMixin, forms.Form):
    def __init__(self, suitability, language='de', *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = models.MapLabels.objects.filter(suitability=suitability).order_by("order_position")
        default_attrs = {
            "data_range_min": 0,
            "data_range_max": 5,
            "string_label": True,
            "reset": True,
            "class": "hiddeninput",
        }
        for label in labels:
            # Pre-fill with default or existing project score  
            attrs = default_attrs.copy()
            
            attrs["data_cur_val"] = label.default_score
            attrs["data_default_value"] = label.default_score
            attrs["id"] = f"id_{suitability}_{label.name}"
            attrs["name"] = f"{suitability}_{label.name}"
            label_field = f"label_{language}"
            label_text = getattr(label, label_field, label.name)

            self.fields[label.name] = forms.IntegerField(
                required=False,
                widget=CustomSimpleSliderWidget(attrs=attrs),
                label=label_text,
            )

        # Crispy forms helper
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = f'{suitability}-suitability-form'
        self.helper.form_class = 'form-horizontal suitability-form'
        self.helper.label_class = 'col-lg-4 col-md-4 col-sm-auto'
        self.helper.field_class = 'col-lg-8 col-md-8 col-sm-auto'
        self.helper.add_input(Button(
            f'{suitability}-reset', 
            'Reset', 
            css_class='btn-secondary reset-all'
        ))


class DrainageProbabilityFilterForm(InfoLabelFormMixin, forms.Form):
    threshold  = forms.IntegerField(
        min_value=0, 
        max_value=100, 
        # initial=25, 
        widget=CustomSimpleSliderWidget(attrs={
            "id": "id_drainage_threshold",
            "name": "drainage_threshold",
            "reset": True,
            "data_range_min": 0,
            "data_range_max": 100,
            "data_cur_val": 40,
            "data_default_value": 40,
            "units": "%",
        }),
        label="Schwellenwert",
        required=False,
        help_text= (
            "Schwellenwert für die dargestellte Entwässerungswahrscheinlichkeit."
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'drainage-threshold-filter-form'
        self.helper.form_class = 'form-horizontal threshold-form'
        self.helper.label_class = 'col-lg-2 col-md-2 col-sm-auto'
        self.helper.field_class = 'col-lg-10 col-md-10 col-sm-auto'
        self.helper.layout = Layout(*[Field(name) for name in self.fields])


class DrainageNetworkFilterForm(InfoLabelFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Loop types
        for network_type in models.DrainageNetworkType.objects.prefetch_related('details'):
            # Create a heading (optional, useful in template)
            self.fields[f"group_{network_type.id}"] = forms.CharField(
                initial=network_type.name_de,
                required=False,
                widget=forms.HiddenInput()
            )

            # Loop details and create checkboxes
            for detail in network_type.details.all():
                field_name = f"detail_{detail.id}"
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    initial=True,
                    label=detail.name_de,
                    widget=forms.CheckboxInput(attrs={
                        "data-network-type-detail": detail.id,
                        "data-network-type": network_type.id,
                        "prefix": 'drainage_network',
                        "name": 'detail',
                        "value": detail.id,
                    })
                )


###### Download / Result forms #########

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
        self.helper.add_input(Button(f'{toolbox_type}-results', 'Herunterladen', css_class='btn-primary download-results', **{'data-type': toolbox_type}))


EPSG_CHOICES = [
    ('25833', 'EPSG:25833'),
    ('4326', 'EPSG:4326')
] 
class InfiltrationResultDownloadForm(ResultForm):
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    result = forms.MultipleChoiceField(
        label="Ergebnisdarstellung", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', ' als GeoJSON')
        ],
        initial=['result_shp'],
    )

    sinks = forms.MultipleChoiceField(
        label="Senken", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'Polygone als Shapefile'),
            ('gjson', 'Polygone als GeoJSON'),
            ('pt_shp', 'Punkte als Shapefile'),
            ('pt_gjson', 'Punkte als GeoJSON'),    
        ],
        # initial=['sinks_shp']
    )
    enlarged_sinks = forms.MultipleChoiceField(
        label="Vergrößerte Senken", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'Polygone als Shapefile'),
            ('gjson', 'Polygone als GeoJSON'),
            ('pt_shp', 'Punkte als Shapefile'),
            ('pt_gjson', 'Punkte als GeoJSON'),
        ],
        # initial=['shp'],
    )

    waterbodies = forms.MultipleChoiceField(
        label="Gewässer", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', ' als GeoJSON'),
        ],
        initial=['shp'],
    )

    
    timeseries = forms.MultipleChoiceField(
        label="Ökologischer Mindestabfluss",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('csv', 'als CSV-Datei'),
        ]
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='infiltration', **kwargs)

    

waterbodies = forms.MultipleChoiceField(
        label="Gewässer", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', ' als GeoJSON'),
        ],
        initial=['shp'],
    )
class SiekerSurfaceWaterResultDownloadForm(ResultForm):
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    
    lakes = forms.MultipleChoiceField(
        label="Seen", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
            ('csv', 'als CSV-Datei'),
        ],
        initial=['lakes_shp'],
    )
    stations = forms.MultipleChoiceField(
        label="Pegelstationen",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'als Shapefile'),  
            ('gjson', 'als GeoJSON'),   
            ('level_csv', 'als CSV-Datei'),   
        ],
        initial=['shp'],
    )
    timeseries = forms.MultipleChoiceField(
        label="Pegelzeitreihen",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('csv', 'als CSV-Datei'),
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='sieker_surface_water', **kwargs)



class SiekerSinkDownloadForm(ResultForm):
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    
    result = forms.MultipleChoiceField(
        label="Ergebnisdarstellung", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', ' als GeoJSON'),
        ],
        initial=['shp'],
    )
    
    sinks = forms.MultipleChoiceField(
        label="Senken", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'Polygone als Shapefile'),
            ('gjson', 'Polygone als GeoJSON'),
            ('pt_shp', 'Punkte als Shapefile'),
            ('pt_gjson', 'Punkte als GeoJSON'),
        ]
    )

    waterbodies = forms.MultipleChoiceField(
        label="Gewässer", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', ' als GeoJSON'),
        ],
        initial=['shp'],
    )

    
    timeseries = forms.MultipleChoiceField(
        label="Ökologischer Mindestabfluss",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,
        choices=[
            ('csv', 'als CSV-Datei'),
        ]
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='infiltration', **kwargs)



class SiekerGekDownloadForm(ResultForm): #######
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    
    map = forms.MultipleChoiceField(
        label="Karte", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
        ],
        initial=['shp'],
    )

    geks = forms.MultipleChoiceField(
        label="Maßnahmen", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('csv', 'als CSV-Datei'),
        ],
        initial=['csv'],
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='sieker_gek', **kwargs)


class SiekerWetlandDownloadForm(ResultForm): #######
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    
    wetlands = forms.MultipleChoiceField(
        label="Feuchtgebiete", 
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'Polygone als Shapefile'),
            ('gjson', 'Polygone als GeoJSON'),
            ('csv', 'als CSV-Datei'),
        ],
        initial=['shp'],
    )
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='sieker_wetland', **kwargs)

    
class SiekerDrainageDownloadForm(ResultForm): #######
    crs = forms.ChoiceField(
        label='CRS',
        widget=forms.RadioSelect,
        choices = EPSG_CHOICES,
        initial='25833',
        required=False,      
    )
    
    probability_raster = forms.MultipleChoiceField(
        label="Wahrscheinlichkeiten",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,  
        choices=[
            ('raster_tif', 'als GeoTIFF Datei'),
        ],
        initial=['raster_tif']
    )

    drainage_network = forms.MultipleChoiceField(
        label="Entwässerungsnetz",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,   
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
        ],
        initial=['shp'],
    )

    drained_areas = forms.MultipleChoiceField(
        label="Entwässerte Flächen",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('shp', 'als Shapefile'),
            ('gjson', 'als GeoJSON'),
        ],
        initial=['shp'],
    )
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='drainage', **kwargs)



class InjectionDownloadForm(ResultForm): #######
    
    raster = forms.MultipleChoiceField(
        label="Rasterdaten",
        required=False,
        widget=CheckboxSelectMultipleWithAttrs,        
        choices=[
            ('result_raster', 'Ergebnis als Rasterdatei (GeoTIFF)'),
        ],
        initial=['result_raster']
    )
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, toolbox_type='injection', **kwargs)