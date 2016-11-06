import logging

from django.contrib import messages

from play_pi.utils import mpd_client


logger = logging.getLogger(__name__)


def mpd_status(request):
    try:
        with mpd_client() as client:
            return {
                'mpd_status': client.status(),
            }
    except Exception as e:
        error_message = u'Error occurred while getting MPD status: {}'.format(e)
        logger.error(error_message)
        messages.error(request, error_message)
        return {}
