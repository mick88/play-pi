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
    PLAYLIST = [{'pos': '0', 'file': 'http://localhost:8000/get_stream/2002/', 'id': '14'}, {'pos': '1', 'file': 'http://localhost:8000/get_stream/1970/', 'id': '15'}, {'pos': '2', 'file': 'http://localhost:8000/get_stream/1640/', 'id': '16'}, {'pos': '3', 'file': 'http://localhost:8000/get_stream/1736/', 'id': '17'}, {'pos': '4', 'file': 'http://localhost:8000/get_stream/1895/', 'id': '18'}, {'pos': '5', 'file': 'http://localhost:8000/get_stream/1955/', 'id': '19'}, {'pos': '6', 'file': 'http://localhost:8000/get_stream/1744/', 'id': '20'}, {'pos': '7', 'file': 'http://localhost:8000/get_stream/1828/', 'id': '21'}, {'pos': '8', 'file': 'http://localhost:8000/get_stream/1366/', 'id': '22'}, {'pos': '9', 'file': 'http://localhost:8000/get_stream/1425/', 'id': '23'}, {'pos': '10', 'file': 'http://localhost:8000/get_stream/2001/', 'id': '24'}, {'pos': '11', 'file': 'http://localhost:8000/get_stream/1389/', 'id': '25'}, {'pos': '12', 'file': 'http://localhost:8000/get_stream/1973/', 'id': '26'}, {'pos': '13', 'file': 'http://localhost:8000/get_stream/1575/', 'id': '27'}, {'pos': '14', 'file': 'http://localhost:8000/get_stream/1971/', 'id': '28'}, {'pos': '15', 'file': 'http://localhost:8000/get_stream/1333/', 'id': '29'}, {'pos': '16', 'file': 'http://localhost:8000/get_stream/1248/', 'id': '30'}, {'pos': '17', 'file': 'http://localhost:8000/get_stream/1865/', 'id': '31'}, {'pos': '18', 'file': 'http://localhost:8000/get_stream/1962/', 'id': '32'}, {'pos': '19', 'file': 'http://localhost:8000/get_stream/2005/', 'id': '33'}, {'pos': '20', 'file': 'http://localhost:8000/get_stream/1508/', 'id': '34'}, {'pos': '21', 'file': 'http://localhost:8000/get_stream/2013/', 'id': '35'}, {'pos': '22', 'file': 'http://localhost:8000/get_stream/1777/', 'id': '36'}, {'pos': '23', 'file': 'http://localhost:8000/get_stream/1799/', 'id': '37'}, {'pos': '24', 'file': 'http://localhost:8000/get_stream/1526/', 'id': '38'}, {'pos': '25', 'file': 'http://localhost:8000/get_stream/1776/', 'id': '39'}, {'pos': '26', 'file': 'http://localhost:8000/get_stream/1979/', 'id': '40'}, {'pos': '27', 'file': 'http://localhost:8000/get_stream/1956/', 'id': '41'}, {'pos': '28', 'file': 'http://localhost:8000/get_stream/2010/', 'id': '42'}, {'pos': '29', 'file': 'http://localhost:8000/get_stream/1334/', 'id': '43'}, {'pos': '30', 'file': 'http://localhost:8000/get_stream/1335/', 'id': '44'}, {'pos': '31', 'file': 'http://localhost:8000/get_stream/1995/', 'id': '45'}, {'pos': '32', 'file': 'http://localhost:8000/get_stream/1836/', 'id': '46'}, {'pos': '33', 'file': 'http://localhost:8000/get_stream/1718/', 'id': '47'}, {'pos': '34', 'file': 'http://localhost:8000/get_stream/1994/', 'id': '48'}]

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

    def playlistinfo(self):
        return self.PLAYLIST

    def addid(self, url, position=None):
        if position is None:
            position = len(self.PLAYLIST)
        item = {
            'pos': position,
            'id': position,
            'file': url,
        }
        self.PLAYLIST.insert(position, item)
        return position + 1

    def clear(self):
        del self.PLAYLIST[:]

    def deleteid(self, mpd_id):
        for item in self.PLAYLIST:
            if item['id'] == mpd_id:
                self.PLAYLIST.remove(item)

    def play(self):
        self.pause(0)
