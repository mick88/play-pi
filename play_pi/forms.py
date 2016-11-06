from __future__ import unicode_literals

from django import forms
from django.db.models.query_utils import Q
from django.forms.widgets import PasswordInput

from play_pi.models import GoogleCredentials, Track


class GoogleCredentialsForm(forms.ModelForm):
    class Meta:
        model = GoogleCredentials
        fields = '__all__'
        # exclude = 'password',
        widgets = {
            'password': PasswordInput(),
        }


class SearchForm(forms.Form):
    q = forms.CharField(max_length=70, label='Search...')

    def build_track_q(self):
        """
        Builds Q object for filtering tracks
        """
        query = self.cleaned_data['q']
        q = Q()
        q |= Q(name__icontains=query)
        q |= Q(artist__name__icontains=query)
        return q

    def filter(self, qs):
        """
        Filters queryset by filters specified in this form
        """
        return qs.filter(self.build_track_q())
