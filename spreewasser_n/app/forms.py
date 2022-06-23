from django import forms
from django.core import  validators



class FormSidebar(forms.Form):
    name = forms.CharField(label='label')
    email = forms.EmailField()
    text = forms.CharField(widget=forms.Textarea)
    botcatcher = forms.CharField(required=False,
                        widget=forms.HiddenInput,
                        validators=[validators.MaxLengthValidator(0)]
        )
                             
    #TODO not working

    def clean_botcather(self):
        botcatcher = self.cleaned_data['botcatcher']
        if len(botcatcher) > 0:
            raise (forms.ValidationError("GOTCHA BOT!"))
        return botcatcher