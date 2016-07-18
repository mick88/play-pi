import logging

import mpd
from django.apps import apps
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse

from play_pi.models import Track, RadioStation

logger = logging.getLogger(__name__)

client = None


def get_gplay_url(stream_id):
    app = apps.get_app_config('play_pi')
    api = app.get_api()
    return api.get_stream_url(stream_id, app.get_credentials().device_id)


def mpd_play(tracks):
    client = get_client()
    site = Site.objects.get_current()
    base_address = 'http://{}'.format(site.domain)
    client.clear()
    for track in tracks:
        path = reverse('get_stream', args=[track.id, ])
        url = base_address + path
        track.mpd_id = client.addid(url)
        track.save()
    client.play()


def get_client():
    global client
    if client is None:
        client = mpd.MPDClient()
        client.connect("localhost", 6600)
    return client


def mpd_play_radio(station):
    client = get_client()
    client.clear()
    mpd_id = client.addid(station.url)
    station.mpd_id = mpd_id
    station.save()
    client.play()


def get_currently_playing_track():
    status = get_client().status()
    try:
        mpd_id = int(status['songid'])
    except:
        return {}

    if mpd_id == 0:
        return {}

    try:
        track = Track.objects.get(mpd_id=mpd_id)
        return track
    except Track.DoesNotExist:
        try:
            return RadioStation.objects.get(mpd_id=mpd_id)
        except RadioStation.DoesNotExist:
            return {}
    except MultipleObjectsReturned:
        return {}
