from django.forms.widgets import Input

class UnitInputWrapper(Input):
    input_type = "text"  # Default to "text"

    def __init__(self, widget=None, unit="", attrs=None):
        super().__init__(attrs)
        self.unit = unit
        self.widget = widget or Input(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        html = self.widget.render(name, value, attrs, renderer)
        return f'<div class="input-group">{html}<span class="input-group-text">{self.unit}</span></div>'
