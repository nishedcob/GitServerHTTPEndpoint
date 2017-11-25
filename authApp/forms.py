
from django.forms import ModelForm

from authApp import models


class APITokenForm(ModelForm):
    class Meta:
        model = models.APIToken
        fields = ['app_name', 'expires', 'expire_date']
