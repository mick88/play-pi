from __future__ import unicode_literals
from rest_framework import serializers

from play_pi.models import *
from play_pi.utils import mpd_client, mpd_play

MPD_PAUSE = 'pause'
MPD_STOP = 'stop'
MPD_PLAY = 'play'


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()

    class Meta:
        model = Album
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    album = AlbumSerializer()

    class Meta:
        model = Track
        fields = '__all__'


class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)
    class Meta:
        model = Playlist
        fields = '__all__'


class RadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioStation
        fields = '__all__'


class MpdStatusSerializer(serializers.Serializer):
    volume = serializers.IntegerField(required=False)
    repeat = serializers.NullBooleanField(required=False)
    random = serializers.NullBooleanField(required=False)
    single = serializers.NullBooleanField(required=False)
    consume = serializers.NullBooleanField(required=False)
    playlist = serializers.IntegerField(required=False, read_only=True)
    playlistlength = serializers.IntegerField(required=False, read_only=True)
    state = serializers.ChoiceField(required=False, choices=[MPD_PLAY, MPD_STOP, MPD_PAUSE])
    song = serializers.IntegerField(required=False)
    songid = serializers.IntegerField(required=False)
    nextsong = serializers.IntegerField(required=False)
    nextsongid = serializers.IntegerField(required=False)
    time = serializers.CharField(required=False, help_text='Time elapsed. Post only integer to seek.')
    elapsed = serializers.CharField(required=False, read_only=True)
    duration = serializers.IntegerField(required=False, read_only=True)
    bitrate = serializers.IntegerField(required=False, read_only=True)
    xfade = serializers.IntegerField(required=False)
    mixrampdb = serializers.FloatField(required=False)
    audio = serializers.CharField(required=False, read_only=True)
    error = serializers.CharField(required=False, read_only=True)

    def seek(self, client, time):
        return client.seekcur(time=time)

    # Defines callables (accepting client and value) to set value,
    # or string name of the setter in the client
    SETTERS = {
        'volume': 'setvol',
        'state': lambda client, state: {
            MPD_PLAY: lambda : client.play(),
            MPD_PAUSE: lambda : client.pause(1),
            MPD_STOP: lambda : client.stop(),
        }[state](),
        'songid': lambda client, songid: client.playid(songid),
        'song': lambda client, songid: client.play(songid),
        'time': lambda client, time: client.seekcur(time),
        'xfade': 'crossfade',
    }

    def create(self, validated_data):
        with mpd_client() as client:
            for key, value in validated_data.items():
                if value is not None:
                    if key == 'volume':
                        # Handle volume increments, decrements if original value was prefixed with + or -
                        if self.initial_data['volume'][0] in ('+', '-'):
                            status = client.status()
                            value += int(status['volume'])
                    if isinstance(value, bool):
                        # Cast boolean values to int since MPD doesnt understand booleans
                        value = int(value)
                    setter = self.SETTERS.get(key, key)
                    if callable(setter):
                        setter(client, value)
                    elif isinstance(setter, basestring):
                        setter = getattr(client, setter)
                        setter(value)
                    else:
                        raise ValueError('Unknown action for {}.'.format(key))

            return client.status()


class QueueItemSerializer(serializers.Serializer):
    mpd_id = serializers.IntegerField(read_only=True)
    track = TrackSerializer(required=False)
    radio_station = RadioSerializer(required=False)

    def enqueue(self, client, position=None):
        """Enqueue this item"""
        data = self.initial_data
        if 'track' in data:
            item = Track.objects.get(id=data['track']['id'])
            site = Site.objects.get_current()
            url = 'http://{domain}{stream}'.format(
                domain=site.domain,
                stream=reverse('get_stream', args=[item.id, ])
            )
        elif 'radio_station' in data:
            item = RadioStation.objects.get(id=data['radio_station']['id'])
            url = item.url
        else:
            return None

        item.mpd_id = client.addid(url, position)
        if item.mpd_id is None:
            raise ValueError('Could not add {} to queue'.format(item))
        item.save()
        return item
