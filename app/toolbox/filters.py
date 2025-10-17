
from django_filters import FilterSet
from django.db.models import Min, Max
from django.db.models import Q
# from django_filters import FloatFilter
from django_filters.filters import RangeFilter, ChoiceFilter, MultipleChoiceFilter, ModelMultipleChoiceFilter, NumberFilter
from django_filters.fields import RangeField
from django import forms
from . import models
from .forms import SliderFilterForm
import json
from utils.widgets import CustomRangeSliderWidget, CustomSingleSliderWidget, CustomDoubleSliderWidget, CustomSimpleSliderWidget
import math
# from django_filters import FloatFilter



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
}
class MinMaxRangeFilter(RangeFilter):
    def __init__(self, *args, model=None, field_name=None, widget=None, queryset=None, **kwargs):
        
        self.model = model
        self.field_name = field_name
        self.units = FIELD_UNITS.get(field_name, "")
        self.queryset_for_bounds = queryset  # to be set in FilterSet
        if widget is None:
            widget = CustomDoubleSliderWidget()
        super().__init__(widget=widget, *args, **kwargs)


    def set_bounds(self):
        if not self.queryset_for_bounds or not self.field_name:
            return

        qs = self.queryset_for_bounds.exclude(**{f"{self.field_name}__isnull": True})
        min_val, max_val = None, None

        if self.field_name == 'index_soil':
            values = list(qs.values_list(self.field_name, flat=True))
            int_values = []
            for v in values:
                if (v * 100) < 1:
                    v = 0
                elif (v * 100) > 99:
                    v = 100
                else:
                    v = int(v * 100)
                int_values.append(v)
            if int_values:
                min_val, max_val = min(int_values), max(int_values)
            else:
                min_val, max_val = 0, 100

        else:
            agg = qs.aggregate(min_val=Min(self.field_name), max_val=Max(self.field_name))


            if agg['min_val'] is not None and agg['max_val'] is not None:
                min_val = math.floor(agg['min_val'])
                max_val = math.ceil(agg['max_val'])
            else:
                min_val = 0
                max_val = 1  

        # Assign attributes to widget
        self.field.widget.attrs.update({
            'data_range_min': min_val,
            'data_range_max': max_val,
            'data_cur_min': min_val,
            'data_cur_max': max_val,
            # 'data_range_step': 1,
            'units': self.units,
        })

class SinkFilter(FilterSet):
    area = MinMaxRangeFilter(
        model=models.Sink, 
        field_name='area', 
        label="Area (m²)",
        )
    volume = MinMaxRangeFilter(model=models.Sink, field_name='volume', label="Volume (m³)")
    depth = MinMaxRangeFilter(model=models.Sink, field_name='depth', label="Depth (m)")
    # index_soil = MinMaxRangeFilter(model=models.Sink, field_name='index_soil', label="Soil Index (%)")

    land_use = MultipleChoiceFilter(
        label="Land Use",
        choices=[],  # Will be set in __init__
        # method='filter_land_use',
        widget=forms.CheckboxSelectMultiple,
    )

    
    def __init__(self, *args, queryset=None, **kwargs):
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
    area = MinMaxRangeFilter(model=models.EnlargedSink, field_name='area', label="Area (m²)")
    volume = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume', label="Volume (m³)")
    depth = MinMaxRangeFilter(model=models.EnlargedSink, field_name='depth', label="Depth (m)")
    volume_construction_barrier = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume_construction_barrier', label="Volume Construction Barrier (m³)")
    volume_gained = MinMaxRangeFilter(model=models.EnlargedSink, field_name='volume_gained', label="Volume Gained (m³)")
    # index_soil = MinMaxRangeFilter(model=models.EnlargedSink, field_name='index_soil', label="Soil Index (%)")

    # Placeholder for land_use — choices will be set dynamically
    land_use = MultipleChoiceFilter(
        label="Land Use",
        choices=[],  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, queryset=None, **kwargs):
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
    min_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='min_surplus_volume', label="Min Surplus Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='mean_surplus_volume', label="Mean Surplus Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='max_surplus_volume', label="Max Surplus Volume (m³)")
    plus_days = MinMaxRangeFilter(model=models.Stream, field_name='plus_days', label="Surplus Days")

    distance_to_userfield = NumberFilter(
        label="Distance to userfield (m)",
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
    
    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds()

        prefix = 'stream'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f'{prefix}_{name}'
            field.widget.attrs['name'] = f'{prefix}_{name}'
            field.widget.attrs['prefix'] = prefix


    class Meta:
        model = models.Stream
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm

class LakeFilter(FilterSet):
    min_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='min_surplus_volume', label="Min Surplus Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='mean_surplus_volume', label="Mean Surplus Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=models.Stream, field_name='max_surplus_volume', label="Max Surplus Volume (m³)")
    plus_days = MinMaxRangeFilter(model=models.Stream, field_name='plus_days', label="Surplus Days")
   
    distance_to_userfield = NumberFilter(
        label="Distance to userfield (m)",
        method='filter_distance_placeholder',
        widget=CustomSimpleSliderWidget(attrs = {
            "id": "lake_distance_to_userfield",
            "name": "lake_distance_to_userfield",
            "prefix": "lake",
            "data_range_min": 0,
            "data_range_max": 2000,
            "data_cur_val": 0,
            "units": "m",
            "class": "hiddeninput",
        }) 
    )
   

    def filter_distance_placeholder(self, queryset, name, value):
        # this is just a placeholder.
        return queryset
    
    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
                filter_.queryset_for_bounds = queryset
                filter_.set_bounds()

        prefix = 'lake'
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
    # badesee = MultipleChoiceFilter(
    #     label="Badesee",
    #     choices=[('yes', 'Ja'), ('no', 'Nein')],
    #     method='filter_bathing_lake',
    #     widget=forms.CheckboxSelectMultiple,
    # )

    # def filter_bathing_lake(self, queryset, name, value):
    #     if value == 'yes':
    #         return queryset.filter(badesee=True)
    #     elif value == 'no':
    #         return queryset.filter(badesee=False)
    #     return queryset

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
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
    area = MinMaxRangeFilter(
        model=models.Sink, 
        field_name='area', 
        label="Fläche (m²)",
        )
    volume = MinMaxRangeFilter(model=models.SiekerSink, field_name='volume', label="Volumen (m³)")
    depth = MinMaxRangeFilter(model=models.SiekerSink, field_name='depth', label="Depth (m)")
    avg_depth = MinMaxRangeFilter(model=models.SiekerSink, field_name='avg_depth', label="Average Depth (m)")
    urbanarea_percent = MinMaxRangeFilter(model=models.SiekerSink, field_name='urbanarea_percent', label="Urban Area (%)")
    wetlands_percent = MinMaxRangeFilter(model=models.SiekerSink, field_name='wetlands_percent', label="Wetlands Area (%)")
   
    feasibility = MultipleChoiceFilter(
        label="Umsetzbarkeit",
        choices=[('leicht', 'leicht'), ('mittel', 'mittel'), ('schwierig', 'schwierig')],  
        widget=forms.CheckboxSelectMultiple,
    )

    
    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        for name, filter_ in self.filters.items():
            if isinstance(filter_, MinMaxRangeFilter):
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

    def __init__(self, *args, **kwargs):
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
            "name": "feasibilty",
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
        

   