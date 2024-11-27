from django import forms

class SingleRowTextarea(forms.Textarea):
    """
    By default, textareas are 10 lines high. This widget makes them only 1 line high."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).setdefault('rows', 1)
        super().__init__(*args, **kwargs)