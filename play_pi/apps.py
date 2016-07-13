from __future__ import unicode_literals

from django.apps.config import AppConfig
from play_pi.models import GoogleCredentials
from django.db.utils import OperationalError


class PlayPiApp(AppConfig):
    name = 'play_pi'
    label = 'play_pi'
    verbose_name = 'Play Pi'

    def ready(self):
        super(PlayPiApp, self).ready()
        Track = self.get_model('Track')
        try:
            Track.objects.filter(mpd_id__gt=0).update(mpd_id=0)
        except OperationalError:
            # Will happen if migrations have not ran yet
            pass

    def get_credentials(self):
        return GoogleCredentials.objects.enabled().get()

    def get_api(self):
        if not hasattr(self, 'api'):
            from gmusicapi import Mobileclient
            self.api = Mobileclient()
            credentials = self.get_credentials()
            self.api.login(credentials.username, credentials.password, credentials.device_id)
        return self.api
