from __future__ import unicode_literals

from mpd import MPDClient

from api.serializers import MPD_PAUSE,MPD_PLAY, MPD_STOP


class MockMpdClient(MPDClient):
    """
    Mock implementation of MPD client used for testing
    """
    status_data = {
        'songid': 1,
        'playlistlength': 1,
        'playlist': 3,
        'repeat': False,
        'consume': False,
        'song': 0,
        'random': False,
        'state': MPD_PLAY,
        'elapsed': u'5373.756',
        'volume': 51,
        'single': False,
        'mixrampdb': 0.0,
        'time': u'5374:0',
        'audio': u'44100:24:2',
        'bitrate': 128,
    }

    def __init__(self, use_unicode=False):
        super(MockMpdClient, self).__init__(use_unicode)
        # Create setters for fields to override MPD methods
        for field_name in 'repeat', 'consume', 'random', 'single':
            setter = self.create_setter(field_name)
            setattr(self, field_name, setter)

    def setvol(self, volume):
        self.status_data['volume'] = volume

    def pause(self, pause):
        self.status_data['state'] = MPD_PAUSE if pause else MPD_PLAY

    def stop(self):
        self.status_data['state'] = MPD_STOP

    def create_setter(self, field_name):
        """ Creates a setter method for the field and returns it """
        def setter(value):
            self.status_data[field_name] = value
        setter.__name__ = str(field_name)
        return setter

    def connect(self, host, port, timeout=None):
        pass

    def disconnect(self):
        pass

    def status(self):
        return self.status_data
