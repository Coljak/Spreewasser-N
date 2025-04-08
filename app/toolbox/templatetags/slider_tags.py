from django import template

register = template.Library()

@register.inclusion_tag('widgets/range_slider.html')
def render_range_slider(
    slider_id,
    label_left,
    label_right,
    min_value,
    max_value,
    initial_min,
    initial_max,
    unit=""
):
    return {
        'slider_id': slider_id,
        'label_left': label_left,
        'label_right': label_right,
        'min_value': min_value,
        'max_value': max_value,
        'initial_min': initial_min,
        'initial_max': initial_max,
        'unit': unit,
    }
