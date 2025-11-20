

from django.db.models import Min, Max
from django.db.models import Q
from django_filters import FilterSet
from django_filters.filters import RangeFilter, ChoiceFilter, MultipleChoiceFilter, ModelMultipleChoiceFilter, NumberFilter

from django import forms
from toolbox import utils
from . import models
from .forms import SliderFilterForm, CheckboxSelectMultipleWithAttrs
import json
from utils.widgets import CustomRangeSliderWidget, CustomSingleSliderWidget, CustomDoubleSliderWidget, CustomSimpleSliderWidget
import math
from datetime import datetime




FIELD_UNITS = {
    "area": "m²",
    "volume": "m³",
    "volume_construction_barrier": "m³",
    "volume_gained": "m³",
    "min_surplus_volume": "m³",
    "max_surplus_volume": "m³",
    "mean_surplus_volume": "m³",
    "depth": "m",
    "index_soil": "%",
    'depth': "m",
    'avg_depth': "m",
    'urbanarea_percent': "%",
    'wetlands_percent': "%",
    'd_max_m': "m",
    'vol_mio_m3': "Mio m³",
    'area_ha': "ha",
    'costs': '€',
    'plus_days': 'Tage/Jahr',
}



def export_bounds_for_project(filter_set, metadata={}):
    for name, filter_ in filter_set.filters.items():
        prefix = filter_set.form.fields[name].widget.attrs.get('prefix')
        if not prefix:
            continue
        base_name = f'{prefix}_{name}'
        # --- Range filters ---
        if isinstance(filter_, MinMaxRangeFilter):
            # first determine bounds

            
            if filter_.precomputed_bounds and filter_.field_name in filter_.precomputed_bounds:
                min_val, max_val = filter_.precomputed_bounds[filter_.field_name]
            else:
                # fallback to widget (already set by set_bounds())
                attrs = filter_.field.widget.attrs
                min_val = attrs.get("data_range_min")
                max_val = attrs.get("data_range_max")

            metadata.update({
                f"{base_name}_min": str(min_val),
                f"{base_name}_max": str(max_val),
            })
            continue

        # ---single-sliders
        if isinstance(filter_, NumberFilter):
            attrs = filter_.field.widget.attrs
            cur_val = attrs.get("data_cur_val", 0)
            metadata.update({
                base_name: str(cur_val),
            })
            continue


        # --- Multiple-choice filters ---
        field = filter_set.form.fields[name]
        if hasattr(field, "choices"):
            metadata.update({
                base_name: [str(value) for value, _ in field.choices]
            })
            continue


    return metadata


def create_default_project(user_filed, list_of_filters, toolbox_type):
    metadata = {}
    for l in list_of_filters:
        if isinstance(l, FilterSet):
            metadata = export_bounds_for_project(l, metadata)
            
            if toolbox_type == 'drainage' and isinstance(l, DrainageNetworkFilter):
                # Special handling for DrainageNetworkFilter
                for name, field in l.form.fields.items():
                    parent_name = 'parent_' + name
                    parent_id = field.widget.attrs.get('parent')


                    if parent_id:
                        metadata.update({parent_name: [str(parent_id)]})

            
            
        elif isinstance(l, forms.Form) or isinstance(l, forms.ModelForm):
            print("Is Instance of Form or Modelform")
            for _, field in l.fields.items():
                print(field)
                print(field.widget.attrs)
                # sliders:
                if isinstance(field.widget, (CustomRangeSliderWidget, CustomSingleSliderWidget, CustomDoubleSliderWidget, CustomSimpleSliderWidget)):
                    name = field.widget.attrs['name']
                    val = field.widget.attrs['data_cur_val']
                    metadata.update({name: str(val)})
                    continue

                else:
                    print("Not a slider widget")
                    name = field.widget.attrs['name']
                    prefix = field.widget.attrs['prefix']
                    full_name = f"{prefix}_{name}"
                    if isinstance(field.widget, forms.CheckboxSelectMultiple):
                        selected_values = []
                        for value, label in field.choices:
                            # Check if the current choice is selected
                            if field.initial and str(value) in field.initial:
                                selected_values.append(str(value))
                        metadata.update({full_name: selected_values})
                    # else:
                    #     val = field.widget.attrs.get('data_cur_val', '')
                    #     metadata.update({full_name: str(val)})
                # val = field.widget.attrs['data_cur_val']
                # metadata.update({name: str(val)})
    

    project = {
        "userField": user_filed.id if user_filed else None,
        "toolboxType": toolbox_type
    }
    print(project)
    project.update(metadata)
    print(project)
    return project






class MinMaxRangeFilter(RangeFilter):
    def __init__(self, *args, model=None, field_name=None, widget=None, queryset=None, bounds=None, **kwargs):
        self.model = model
        self.field_name = field_name
        self.units = FIELD_UNITS.get(field_name, "")
        self.queryset_for_bounds = queryset
        self.precomputed_bounds = bounds
        if widget is None:
            widget = CustomDoubleSliderWidget()
        super().__init__(widget=widget, *args, **kwargs)

        # Immediately set bounds if precomputed
        if self.precomputed_bounds and self.field_name in self.precomputed_bounds:
            min_val, max_val = self.precomputed_bounds[self.field_name]
            self._apply_widget_bounds(min_val, max_val)

    def set_bounds(self):
        """Compute bounds if not precomputed."""
        # Skip queryset requirement when precomputed bounds are available
        if self.precomputed_bounds and self.field_name in self.precomputed_bounds:
            min_val, max_val = self.precomputed_bounds[self.field_name]
            self._apply_widget_bounds(min_val, max_val)
            return
        
        # otherwise fall back to live computation
        if not self.queryset_for_bounds or not self.field_name:
            return
        
        min_val, max_val = utils.get_bounds(
            self.queryset_for_bounds.exclude(**{f"{self.field_name}__isnull": True}),
            self.field_name
        )
        self._apply_widget_bounds(min_val, max_val)

    def _apply_widget_bounds(self, min_val, max_val):
        self.field.widget.attrs.update({
            'data_range_min': min_val,
            'data_range_max': max_val,
            'data_cur_min': min_val,
            'data_cur_max': max_val,
            'units': self.units,
        })


class SinkFilter(FilterSet):
    area = MinMaxRangeFilter(
        model=models.Sink, 
        field_name='area', 
        label="Fläche",
        )
    volume = MinMaxRangeFilter(model=models.Sink, field_name='volume', label="Volumen")
    depth = MinMaxRangeFilter(model=models.Sink, field_name='depth', label="Tiefe")
    # index_soil = MinMaxRangeFilter(model=models.Sink, field_name='index_soil', label="Soil Index (%)")

    land_use = MultipleChoiceFilter(
        label="Landnutzung",
        choices=[],  # Will be set in __init__
        # method='filter_land_use',
        widget=forms.CheckboxSelectMultiple,
    )

    
    def __init__(self, *args, queryset=None, bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        if queryset is not None:
            land_use_ids = set(
                queryset.exclude(landuse_1__isnull=True).values_list('landuse_1', flat=True)
            ).union(
                queryset.exclude(landuse_2__isnull=True).values_list('landuse_2', flat=True)
            ).union(
                queryset.exclude(landuse_3__isnull=True).values_list('landuse_3', flat=True)
            )

            land_uses = models.Landuse.objects.filter(id__in=land_use_ids)
            choices = sorted([(lu.id, lu.de or f"Landuse {lu.id}") for lu in land_uses])
            self.filters['land_use'].extra['choices'] = choices
            # choices = sorted([(lu, lu) for lu in land_use_values])
            # self.filters['land_use'].extra['choices'] = choices


        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds() 

        prefix = 'sink'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f"{prefix}_{name}"
            field.widget.attrs['name'] = f"{prefix}_{name}"
            field.widget.attrs['prefix'] = prefix


    class Meta:
        model = models.Sink
        fields = ['area', 'volume', 'depth',  'land_use']
        form = SliderFilterForm

class EnlargedSinkFilter(FilterSet):
    area = MinMaxRangeFilter(model=models.EnlargedSink, field_name='area', label="Fläche")
    volume = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume', label="Volumen")
    depth = MinMaxRangeFilter(model=models.EnlargedSink, field_name='depth', label="Tiefe")
    volume_construction_barrier = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume_construction_barrier', label="Volumen der Barriere")
    volume_gained = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume_gained', label="Zusätzliches Volumen")
    # index_soil = MinMaxRangeFilter(model=models.EnlargedSink, field_name='index_soil', label="Soil Index (%)")

    # Placeholder for land_use — choices will be set dynamically
    land_use = MultipleChoiceFilter(
        label="Landnutzung",
        choices=[],  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, queryset=None, bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        # Dynamically set land use choices from queryset
        if queryset is not None:
            land_use_ids = set(
                queryset.exclude(landuse_1__isnull=True).values_list('landuse_1', flat=True)
            ).union(
                queryset.exclude(landuse_2__isnull=True).values_list('landuse_2', flat=True)
            ).union(
                queryset.exclude(landuse_3__isnull=True).values_list('landuse_3', flat=True)
            ).union(
                queryset.exclude(landuse_4__isnull=True).values_list('landuse_4', flat=True)
            )

            land_uses = models.Landuse.objects.filter(id__in=land_use_ids)
            choices = sorted([(lu.id, lu.de or f"Landuse {lu.id}") for lu in land_uses])
            self.filters['land_use'].extra['choices'] = choices


        # Configure range sliders (MinMaxRangeFilter)
        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds() 

        prefix = 'enlarged_sink'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f'{prefix}_{name}'
            field.widget.attrs['name'] = f'{prefix}_{name}'
            field.widget.attrs['prefix'] = prefix

    class Meta:
        model = models.EnlargedSink
        fields = ['area', 'volume', 'depth', 'volume_construction_barrier', 'volume_gained',  'land_use']
        form = SliderFilterForm

    

class StreamFilter(FilterSet):
    min_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='min_surplus_volume', label="Minimales Überschussvolumen")
    mean_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='mean_surplus_volume', label="Mittleres Überschussvolumen")
    max_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='max_surplus_volume', label="Maximales Überschussvolumen")
    plus_days = MinMaxRangeFilter(model=models.Stream, field_name='plus_days', label="Tage mit Überschuss")

    distance_to_userfield = NumberFilter(
        label="Suchradius erweitern",
        method='filter_distance_placeholder',
        widget=CustomSimpleSliderWidget(attrs = {
            "id": "stream_distance_to_userfield",
            "name": "stream_distance_to_userfield",
            "reset": True,
            "prefix": "stream",
            "data_range_min": 0,
            "data_range_max": 2000,
            "data_cur_val": 0,
            "units": "m",
            "class": "hiddeninput",
        }) 
    )
   

    def filter_distance_placeholder(self, queryset, name, value):
        # We don’t filter here – this is just a placeholder.
        return queryset
    
    def __init__(self, *args, queryset=None,  prefix='stream', bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds() 

       
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f'{prefix}_{name}'
            field.widget.attrs['name'] = f'{prefix}_{name}'
            field.widget.attrs['prefix'] = prefix


    class Meta:
        model = models.Stream
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm

class LakeFilter(FilterSet):
    min_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='min_surplus_volume', label="Minimales Überschussvolumen")
    mean_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='mean_surplus_volume', label="Mittleres Überschussvolumen ")
    max_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='max_surplus_volume', label="Maximales Überschussvolumen")
    plus_days = MinMaxRangeFilter(model=models.Stream, field_name='plus_days', label="Tage mit Überschuss")

    distance_to_userfield = NumberFilter(
        label="Suchradius erweitern",
        method='filter_distance_placeholder',
        widget=CustomSimpleSliderWidget(attrs = {
            "id": "lake_distance_to_userfield",
            "name": "lake_distance_to_userfield",
            "prefix": "lake",
            "reset": True,
            "data_range_min": 0,
            "data_range_max": 2000,
            "data_cur_val": 0,
            "units": " m",
            "class": "hiddeninput",
        }) 
    )
   

    def filter_distance_placeholder(self, queryset, name, value):
        # this is just a placeholder.
        return queryset

    def __init__(self, *args, queryset=None, prefix='lake', bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds()



        
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f'{prefix}_{name}'
            field.widget.attrs['name'] = f'{prefix}_{name}'
            field.widget.attrs['prefix'] = prefix


    class Meta:
        model = models.Lake
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm

## Toolbox Sieker Surface Waters
class SiekerLargeLakeFilter(FilterSet):
    area_ha = MinMaxRangeFilter(model=models.SiekerLargeLake, field_name='area_ha', label="Fläche (ha)")
    vol_mio_m3 = MinMaxRangeFilter(model=models.SiekerLargeLake, field_name='vol_mio_m3', label="Volumen (Mio m³)")
    d_max_m = MinMaxRangeFilter(model=models.SiekerLargeLake, field_name='d_max_m', label="Max. Tiefe (m)")


    def __init__(self, *args, queryset=None, bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds() 

        prefix = 'sieker_surface_water'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f"{prefix}_{name}"
            field.widget.attrs['name'] = f"{prefix}_{name}"
            field.widget.attrs['prefix'] = prefix
    class Meta:
        model = models.SiekerLargeLake
        fields = ['area_ha', 'vol_mio_m3', 'd_max_m']
        form = SliderFilterForm
    
## Toolbox Sieker Sinks
class SiekerSinkFilter(FilterSet):

    volume = MinMaxRangeFilter(model=models.SiekerSink, field_name='volume', label="Volumen (m³)")
    depth = MinMaxRangeFilter(model=models.SiekerSink, field_name='depth', label="Tiefe")
    area = MinMaxRangeFilter(model=models.SiekerSink, field_name='area', label="Fläche")
    avg_depth = MinMaxRangeFilter(model=models.SiekerSink, field_name='avg_depth', label="Durchschnittliche Tiefe")
    urbanarea_percent = MinMaxRangeFilter(model=models.SiekerSink, field_name='urbanarea_percent', label="Urbane Fläche")
    wetlands_percent = MinMaxRangeFilter(model=models.SiekerSink, field_name='wetlands_percent', label="Feuchtgebiet")
   
    feasibility = MultipleChoiceFilter(
        label="Umsetzbarkeit",
        choices=[('leicht', 'leicht'), ('mittel', 'mittel'), ('schwierig', 'schwierig')],  
        widget=forms.CheckboxSelectMultiple,
    )


    def __init__(self, *args, queryset=None, bounds=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.precomputed_bounds = bounds
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds() 

        prefix = 'sieker_sink'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f"{prefix}_{name}"
            field.widget.attrs['name'] = f"{prefix}_{name}"
            field.widget.attrs['prefix'] = prefix


    class Meta:
        model = models.SiekerSink
        fields = ['volume', 'depth', 'avg_depth', 'urbanarea_percent', 'wetlands_percent']
        form = SliderFilterForm


class GekRetentionFilter(FilterSet):
    costs = MinMaxRangeFilter(
        model=models.GekRetentionMeasure, 
        field_name='costs', 
        label="Kosten",
        method='filter_by_costs',
    )
    
    # Landuse filter
    landuse = MultipleChoiceFilter(
        choices = [],
        widget=forms.CheckboxSelectMultiple,
        label="Landnutzung",
        method="filter_by_landuse"
    )


    priority = NumberFilter(
        label="Priorität",
        method='filter_priorities',
        widget=CustomSimpleSliderWidget(attrs = {
            # "id": "gek_priority",
            # "name": "gek_priority",
            # "prefix": "gek",
            "data_range_min": 4,
            "data_range_max": 8,
            "string_label": True,
            "data_cur_val": 4,
            "class": "hiddeninput",
        }) 
    )

    class Meta:
        model = models.GekRetention
        fields = ['costs', 'landuse']
        # Use the custom slider form for the range filter
        form = SliderFilterForm

    def __init__(self, *args, bounds=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limit landuse choices to the current queryset
        landuses = (
            models.GekLanduse.objects
            .filter(gek_retention__in=self.queryset)
            .values_list('clc_landuse', 'clc_landuse__label_level_2')
            .distinct()
        )
        self.filters['landuse'].extra['choices'] = [(id, lu) for id, lu in landuses]

        measures_qs = models.GekRetentionMeasure.objects.filter(
            gek_retention__in=self.queryset
        )
        self.filters['costs'].queryset_for_bounds = measures_qs
        self.filters['costs'].precomputed_bounds = bounds
        self.filters['costs'].set_bounds()

        prefix = 'gek'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f"{prefix}_{name}"
            field.widget.attrs['name'] = f"{prefix}_{name}"
            field.widget.attrs['prefix'] = prefix



    def filter_priorities(self, queryset, name, value):
        """
        Filter by priority level.
        `value` is the selected priority level (4, 5, 6, 7, or 8).
        """
        if value is None:
            return queryset

        # Convert value to integer if it's a string
        try:
            value = int(value)
        except ValueError:
            return queryset

        # Filter by priority level
        return queryset.filter(measures__priority__priority_level__gte=value).distinct()

    def filter_by_landuse(self, queryset, name, value):
        # value is a list of selected landuse strings
        return queryset.filter(landuses__clc_landuse__label_level_2__in=value).distinct()
    
    def filter_by_costs(self, queryset, name, value):
        """
        `queryset` is a GekRetention queryset.
        `value` is a 2-tuple or an object with .start/.stop from RangeFilter.
        """
        if not value:
            return queryset

        # support both tuple and .start/.stop
        if hasattr(value, 'start') or hasattr(value, 'stop'):
            min_val = getattr(value, 'start', None)
            max_val = getattr(value, 'stop', None)
        else:
            try:
                min_val, max_val = value
            except Exception:
                return queryset

        q = {}
        if min_val is not None:
            q['measures__costs__gte'] = min_val
        if max_val is not None:
            q['measures__costs__lte'] = max_val

        if not q:
            return queryset

        return queryset.filter(**q).distinct()
    


class HistoricalWetlandsFilter(FilterSet):
    feasibility = NumberFilter(
        label="Machbarkeit",
        method='filter_feasibility',
        widget=CustomSimpleSliderWidget(attrs = {
            "id": "wetland_feasibility",
            "name": "feasibility",
            "prefix": "sieker_wetland",
            "string_label": True,
            "class": "hiddeninput",
        }) 
    )
    

    class Meta:
        model = models.HistoricalWetlands
        fields = ['feasibility']
        # Use the custom slider form for the range filter
        form = SliderFilterForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        ids_feasibilities = models.WetlandFeasibility.objects.values_list('id', flat=True).distinct()
        min_feasibility = min(ids_feasibilities)
        max_feasibility = max(ids_feasibilities)
        # Set widget attributes dynamically
        slider = self.filters['feasibility'].field.widget
        slider.attrs["data_range_min"] = min_feasibility
        slider.attrs["data_range_max"] = max_feasibility
        slider.attrs["data_cur_val"] = min_feasibility
        

# class CheckboxSelectMultipleWithAttrs(forms.CheckboxSelectMultiple):
#     def __init__(self, attrs=None, choice_attrs=None):
#         super().__init__(attrs)
#         self.choice_attrs = choice_attrs or {}

#     def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
#         option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
#         if str(value) in self.choice_attrs:
#             option['attrs'].update(self.choice_attrs[str(value)])
#         return option

class DrainageNetworkFilter(FilterSet):
    # assign the custom widget directly here
    natural_creeks = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )
    non_natural_creeks = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )
    ditches = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )
    pipes = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )
    rivers = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        network_types = models.DrainageNetworkType.objects.filter(
            details__in=queryset
        ).distinct()

        prefix = 'drainage'
        for network_type in network_types:
            details = queryset.filter(network_type=network_type)

            # Build choices
            choices = [(d.id, d.name_de) for d in details]

            # Build per-choice attributes
            choice_attrs = {str(d.id): {'detail': d.name_tag} for d in details}

            # assign choices and per-choice attrs
            field = self.form.fields[network_type.name_tag]
            field.choices = choices
            field.widget.choice_attrs = choice_attrs

            # Also keep your other widget attrs
            field.widget.attrs['parent'] = network_type.id
            field.widget.attrs['prefix'] = prefix
            
            


class DrainedAreaFilter(FilterSet):
    types = MultipleChoiceFilter(
        initial=True,
        label="",
        choices=[],
        widget=CheckboxSelectMultipleWithAttrs(),
    )


    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        # queryset is models.DrainedArea
        drained_area_types = models.DrainedAreaType.objects.filter(
            drainedarea__in=queryset
        ).distinct()
        choice_attrs = {str(d.id): {'drained_area_type': d.name_tag} for d in drained_area_types}
        choices = [(d.id, d.name_de) for d in drained_area_types]
        # self.form.fields['drained_area_types'].choices = drained_area_types.values_list('id', 'name_de')

        self.form.fields['types'].widget.attrs['prefix'] = 'drained_area'
        
        self.form.fields['types'].widget.choice_attrs = choice_attrs
        self.form.fields['types'].choices = choices
        print("DrainedAreaFilter initialized with choices:", choices)



    # class Meta:
    #     model = models.DrainedArea
    #     fields = ['drained_area_types']
    #     form = SliderFilterForm


