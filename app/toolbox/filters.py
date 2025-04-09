
from django_filters import FilterSet
from django_filters.filters import RangeFilter, RangeFilter, ChoiceFilter, MultipleChoiceFilter
from django import forms
from .models import *
from .forms import SliderFilterForm
from .widgets import CustomRangeSliderWidget

class MinMaxRangeFilter(RangeFilter):
    def __init__(self, model=None, field_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-detect min and max from the queryset based on field_name
        if field_name:
            values = model.objects.values_list(field_name, flat=True)
            values = list(filter(None, values))  # remove None/nulls
            if field_name == 'index_soil':  
                int_values = []
                for v in values:
                    if (v * 100) < 1:
                        v = 0
                    elif (v * 100) > 99:
                        v = 100
                    else:
                        v = int(v * 100)
                    int_values.append(v)
                values = int_values
                print('int_values', int_values)

            if values:
                min_value = min(values)
                max_value = max(values)
                self.extra['widget'] = CustomRangeSliderWidget(attrs={
                    'data-range_min': min_value,
                    'data-range_max': max_value
                })

class SinkFilter(FilterSet):
    area = MinMaxRangeFilter(model=Sink4326, field_name='area', label="Area (ha)")
    volume = MinMaxRangeFilter(model=Sink4326, field_name='volume', label="Volume (m³)")
    depth = MinMaxRangeFilter(model=Sink4326, field_name='depth', label="Depth (m)")
    index_soil = MinMaxRangeFilter(model=Sink4326, field_name='index_soil', label="Soil Index (%)")

    # Custom land use filter combining all 3 fields
    LAND_USE_CHOICES = sorted(set(
        Sink4326.objects.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
    ).union(
        Sink4326.objects.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
    ).union(
        Sink4326.objects.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
    ))

    land_use = MultipleChoiceFilter(
        label="Land Use",
        choices=[(lu, lu) for lu in LAND_USE_CHOICES],
        method='filter_land_use',
        widget=forms.CheckboxSelectMultiple
    )

    def filter_land_use(self, queryset, name, value):
        return queryset.filter(
            models.Q(land_use_1=value) | models.Q(land_use_2=value) | models.Q(land_use_3=value)
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    # Custom land use filter combining all 3 fields
    LAND_USE_CHOICES = sorted(set(
        EnlargedSink4326.objects.exclude(land_use_1__isnull=True).values_list('land_use_1', flat=True)
    ).union(
        EnlargedSink4326.objects.exclude(land_use_2__isnull=True).values_list('land_use_2', flat=True)
    ).union(
        EnlargedSink4326.objects.exclude(land_use_3__isnull=True).values_list('land_use_3', flat=True)
    ))

    land_use = MultipleChoiceFilter(
        label="Land Use",
        choices=[(lu, lu) for lu in LAND_USE_CHOICES],
        method='filter_land_use',
        widget=forms.CheckboxSelectMultiple
    )

    def filter_land_use(self, queryset, name, value):
        return queryset.filter(
            models.Q(land_use_1=value) | models.Q(land_use_2=value) | models.Q(land_use_3=value)
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    min_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='min_surplus_volume', label="Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='mean_surplus_volume', label="Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='max_surplus_volume', label="Volume (m³)")
    plus_days = MinMaxRangeFilter(model=Stream4326, field_name='plus_days', label="Days")
   
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    min_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='min_surplus_volume', label="Volume (m³)")
    mean_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='mean_surplus_volume', label="Volume (m³)")
    max_surplus_volume = MinMaxRangeFilter(model=Stream4326, field_name='max_surplus_volume', label="Volume (m³)")
    plus_days = MinMaxRangeFilter(model=Stream4326, field_name='plus_days', label="Days")
   
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        prefix = 'lake'
        for name, field in self.form.fields.items():
            field.widget.attrs['id'] = f'{prefix}_{name}'
            field.widget.attrs['name'] = f'{prefix}_{name}'
            field.widget.attrs['prefix'] = prefix

    class Meta:
        model = Lake4326
        fields = ['min_surplus_volume', 'mean_surplus_volume', 'max_surplus_volume', 'plus_days']
        form = SliderFilterForm