import logging

import mpd
from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.utils import cache
from django.utils.deprecation import MiddlewareMixin

from play_pi.models import Track, RadioStation

logger = logging.getLogger(__name__)


def invalidate_cache(keys=None):
    """
    Clears cache
    Args:
        keys: keys to be cleared or None to clear everything
    """
    if keys is None:
        cache.caches['default'].clear()
    else:
        cache.caches['default'].delete_many(keys)


def invalidates_cache(keys=None):
    """ Invalidates cache each time before function is called """
    def decorator(func):
        def wrapper(*args, **kwargs):
            invalidate_cache(keys)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_gplay_url(stream_id):
    app = apps.get_app_config('play_pi')
    api = app.get_api()
    return api.get_stream_url(stream_id, app.get_credentials().device_id)


def mpd_play(tracks):
    with mpd_client() as client:
        site = Site.objects.get_current()
        base_address = 'http://{}'.format(site.domain)
        client.clear()
        started = False
        for track in tracks:
            path = reverse('get_stream', args=[track.id, ])
            url = base_address + path
            mpd_id = client.addid(url)
            if mpd_id is None:
                raise ValueError('Could not add {} to queue'.format(track))
            track.mpd_id = mpd_id
            track.save()
            if not started:
                client.play()
                started = Track


def mpd_client_enqueue(client, *tracks):
    """ Append tracks to the queue without actually playing them """
    site = Site.objects.get_current()
    base_address = 'http://{}'.format(site.domain)
    for track in tracks:
        if isinstance(track, RadioStation):
            url = track.url
        else:
            path = reverse('get_stream', args=[track.id, ])
            url = base_address + path
        track.mpd_id = client.addid(url)
        if track.mpd_id is None:
            raise ValueError('Could not add {} to queue'.format(track))
        track.save()


def mpd_enqueue(*tracks):
    """ Append tracks to the queue without actually playing them """
    with mpd_client() as client:
        mpd_client_enqueue(client, *tracks)


class mpd_client(object):
    """
    Create mpd connection for the statement and gracefully close when done
    """
    def __enter__(self):
        self.client = mpd.MPDClient()
        self.client.connect(settings.MPD_ADDRESS, settings.MPD_PORT, settings.MPD_TIMEOUT)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.disconnect()


def mpd_play_radio(station):
    with mpd_client() as client:
        client.clear()
        mpd_id = client.addid(station.url)
        if mpd_id is None:
            raise ValueError('Could not play {}'.format(station))
        station.mpd_id = mpd_id
        station.save()
        client.play()


def get_currently_playing_track():
    with mpd_client() as client:
        status = client.status()

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


class PlayPiMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['AppName'] = 'play_pi'
        # Copy version information from Dealer middleware
        response['AppVersion'] = request.tag
        response['AppRevision'] = request.revision
        return response