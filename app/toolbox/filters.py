
from django_filters import FilterSet
from django.db.models import Min, Max
from django.db.models import Q
# from django_filters import FloatFilter
from django_filters.filters import RangeFilter, ChoiceFilter, MultipleChoiceFilter, NumberFilter
from django_filters.fields import RangeField
from django import forms
from .models import *
from .forms import SliderFilterForm, SingleWidgetForm
from .widgets import CustomRangeSliderWidget, CustomSingleSliderWidget
import math
# from django_filters import FloatFilter

# class MinMaxRangeFilter(RangeFilter):
#     def __init__(self, model=None, field_name=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Auto-detect min and max from the queryset based on field_name
#         if field_name:
#             values = model.objects.values_list(field_name, flat=True)
#             values = list(filter(None, values))  # remove None/nulls
#             if field_name == 'index_soil':  
#                 int_values = []
#                 for v in values:
#                     if (v * 100) < 1:
#                         v = 0
#                     elif (v * 100) > 99:
#                         v = 100
#                     else:
#                         v = int(v * 100)
#                     int_values.append(v)
#                 values = int_values
#                 # print('int_values', int_values)

#             if values:
#                 min_value = min(values)
#                 max_value = max(values)
#                 self.extra['widget'] = CustomRangeSliderWidget(attrs={
#                     'data-range_min': min_value,
#                     'data-range_max': max_value
#                 })

class MinMaxRangeFilter(RangeFilter):
    def __init__(self, *args, model=None, field_name=None, **kwargs):
        self.model = model
        self.field_name = field_name
        self.queryset_for_bounds = None  # to be set in FilterSet
        super().__init__(*args, **kwargs)

        self.extra['widget'] = CustomRangeSliderWidget()

    def set_bounds(self):
        if not self.queryset_for_bounds or not self.field_name:
            return

        qs = self.queryset_for_bounds.exclude(**{f"{self.field_name}__isnull": True})

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
                max_val = 1  # Avoid 0 range

            # min_val = agg.get("min_val", 0)
            # max_val = agg.get("max_val", 100)

        # Assign attributes directly
        self.field.widget.attrs.update({
            'data-range_min': min_val,
            'data-range_max': max_val,
        })

class SinkFilter(FilterSet):
    area = MinMaxRangeFilter(model=Sink4326, field_name='area', label="Area (ha)")
    volume = MinMaxRangeFilter(model=Sink4326, field_name='volume', label="Volume (m³)")
    depth = MinMaxRangeFilter(model=Sink4326, field_name='depth', label="Depth (m)")
    index_soil = MinMaxRangeFilter(model=Sink4326, field_name='index_soil', label="Soil Index (%)")

    land_use = MultipleChoiceFilter(
        label="Land Use",
        choices=[],  # Will be set in __init__
        # method='filter_land_use',
        widget=forms.CheckboxSelectMultiple,
    )

    
    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, queryset=queryset, **kwargs)

        if queryset is not None:
            land_use_values = set(
                queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
            ).union(
                queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
            ).union(
                queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
            )
            choices = sorted([(lu, lu) for lu in land_use_values])
            self.filters['land_use'].extra['choices'] = choices


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
        model = Sink4326
        fields = ['area', 'volume', 'depth', 'index_soil', 'land_use']
        form = SliderFilterForm
class EnlargedSinkFilter(FilterSet):
    area = MinMaxRangeFilter(model=EnlargedSink4326, field_name='area', label="Area (ha)")
    volume = MinMaxRangeFilter(model=EnlargedSink4326, field_name='volume', label="Volume (m³)")
    depth = MinMaxRangeFilter(model=EnlargedSink4326, field_name='depth', label="Depth (m)")
    volume_construction_barrier = MinMaxRangeFilter(model=EnlargedSink4326, field_name='volume_construction_barrier', label="Volume Construction Barrier (m³)")
    volume_gained = MinMaxRangeFilter(model=EnlargedSink4326, field_name='volume_gained', label="Volume Gained (m³)")
    index_soil = MinMaxRangeFilter(model=EnlargedSink4326, field_name='index_soil', label="Soil Index (%)")

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
            land_use_values = set(
                queryset.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
            ).union(
                queryset.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
            ).union(
                queryset.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
            ).union(
                queryset.exclude(land_use_4__isnull=True).values_list('land_use_4', flat=True)
            )
            choices = sorted([(lu, lu) for lu in land_use_values])
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
        model = EnlargedSink4326
        fields = ['area', 'volume', 'depth', 'volume_construction_barrier', 'volume_gained', 'index_soil', 'land_use']
        form = SliderFilterForm



class StreamFilter(FilterSet):
    min_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='min_surplus_volume', label="Min Surplus Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='mean_surplus_volume', label="Mean Surplus Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='max_surplus_volume', label="Max Surplus Volume (m³)")
    plus_days = MinMaxRangeFilter(model=Stream4326, field_name='plus_days', label="Surplus Days")

    distance_to_userfield = NumberFilter(
        label="Distance to userfield (m)",
        method='filter_distance_placeholder',
        widget=CustomSingleSliderWidget(attrs = {
            "data_range_min": 0,
            "data_range_max": 2000,
            "data_cur_val": 0,
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
        model = Stream4326
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm

class LakeFilter(FilterSet):
    min_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='min_surplus_volume', label="Min Surplus Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='mean_surplus_volume', label="Mean Surplus Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='max_surplus_volume', label="Max Surplus Volume (m³)")
    plus_days = MinMaxRangeFilter(model=Stream4326, field_name='plus_days', label="Surplus Days")
   
    
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
        model = Lake4326
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm