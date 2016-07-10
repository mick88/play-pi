from __future__ import unicode_literals

from django.apps.config import AppConfig


class PlayPiApp(AppConfig):
    name = 'play_pi'
    label = 'play_pi'
    verbose_name = 'Play Pi'

    def ready(self):
        super(PlayPiApp, self).ready()
        Track = self.get_model('Track')
        Track.objects.filter(mpd_id__gt=0).update(mpd_id=0)
