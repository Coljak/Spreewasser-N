from django.forms.widgets import HiddenInput
from django_filters.widgets import RangeWidget

class CustomRangeSliderWidget(RangeWidget):
    template_name = 'forms/widgets/range-slider.html'

    def __init__(self, attrs=None):
        widgets = (HiddenInput(), HiddenInput())
        super(RangeWidget, self).__init__(widgets, attrs)
        # default_attrs = {
        #     "data-range_min": 0,
        #     "data-range_max": 1000,
        #     "data-cur_min": 0,
        #     "data-cur_max": 1000,
        #     "class": "hiddeninput",
        # }
        # if attrs:
        #     default_attrs.update(attrs)
        # super().__init__(attrs=default_attrs)


    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        
        # Safely extract range bounds
        cur_min = ctx['widget']['attrs'].get('data-range_min', 0)
        cur_max = ctx['widget']['attrs'].get('data-range_max', 0)

        # Optionally override with current value if available
        if isinstance(value, (list, tuple)) and len(value) == 2:
            if value[0] is not None:
                cur_min = value[0]
            if value[1] is not None:
                cur_max = value[1]

        # Update widget attributes for frontend JS
        ctx['widget']['attrs'].update({
            'data-cur_min': cur_min,
            'data-cur_max': cur_max,
        })

        base_id = ctx['widget']['attrs']['id']
        for swx, subwidget in enumerate(ctx['widget']['subwidgets']):
            subwidget['attrs']['id'] = base_id + "_" + self.suffixes[swx]
        
        ctx['widget']['value_text'] = f"{cur_min} - {cur_max}"
        return ctx

    
class CustomSingleSliderWidget(HiddenInput):
    template_name = "forms/widgets/single-slider.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "data_range_min": 0,
            "data_range_max": 1000,
            "data_cur_val": 0,
            "class": "hiddeninput",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    