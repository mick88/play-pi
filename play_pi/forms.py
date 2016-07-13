from __future__ import unicode_literals

from django import forms
from django.forms.widgets import PasswordInput

from play_pi.models import GoogleCredentials


class GoogleCredentialsForm(forms.ModelForm):
    class Meta:
        model = GoogleCredentials
        fields = '__all__'
        # exclude = 'password',
        widgets = {
            'password': PasswordInput(),
        }