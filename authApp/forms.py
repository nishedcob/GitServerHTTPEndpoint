
from django.forms import ModelForm, DateTimeInput

from authApp import models


class APITokenForm(ModelForm):
    class Meta:
        model = models.APIToken
        fields = ['app_name', 'expires', 'expire_date']
        widgets = {
            'expire_date': DateTimeInput(format='%m/%d/%Y %H:%M')
        }
