from django import forms

class SingleRowTextarea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).setdefault('rows', 1)
        super().__init__(*args, **kwargs)