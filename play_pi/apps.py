from __future__ import unicode_literals

from django.apps.config import AppConfig
from django.db.models import Q
from django.db.utils import OperationalError



class PlayPiApp(AppConfig):
    name = 'play_pi'
    label = 'play_pi'
    verbose_name = 'Play Pi'

    def ready(self):
        from play_pi.models import RadioStation
        from play_pi.utils import mpd_client
        super(PlayPiApp, self).ready()
        Track = self.get_model('Track')
        try:
            with mpd_client() as client:
                playlist = client.playlistinfo()
                mpd_ids = tuple(int(song['id']) for song in playlist)
            q = Q(mpd_id__gt=0) & ~Q(mpd_id__in=mpd_ids)
            Track.objects.filter(q).update(mpd_id=0)
            RadioStation.objects.filter(q).update(mpd_id=0)
        except OperationalError:
            # Will happen if migrations have not ran yet
            pass

    def get_credentials(self):
        from play_pi.models import GoogleCredentials
        return GoogleCredentials.objects.enabled().get()

    def get_api(self):
        if not hasattr(self, 'api'):
            from gmusicapi import Mobileclient
            self.api = Mobileclient()
            credentials = self.get_credentials()
            login = self.api.login(credentials.username, credentials.password, credentials.device_id)
            if not login:
                raise Exception('Login error')
        return self.api
