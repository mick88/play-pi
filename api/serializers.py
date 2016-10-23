from __future__ import unicode_literals
from rest_framework import serializers

from play_pi.models import *
from play_pi.utils import mpd_client

MPD_PAUSE = 'pause'
MPD_STOP = 'stop'
MPD_PLAY = 'play'


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()

    class Meta:
        model = Album


class TrackSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()
    album = AlbumSerializer()

    class Meta:
        model = Track


class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)
    class Meta:
        model = Playlist


class RadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioStation


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
            MPD_PLAY: lambda : client.pause(0),
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
    mpd_id = serializers.IntegerField()
    track = TrackSerializer(required=False)
    radio_station = RadioSerializer(required=False)