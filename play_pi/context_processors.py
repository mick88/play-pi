import mpd

from play_pi.utils import mpd_client


def mpd_status(request):
    with mpd_client() as client:
        return {
            'mpd_status': client.status(),
        }
