from __future__ import unicode_literals

from django.apps.config import AppConfig
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
