from __future__ import unicode_literals
from rest_framework import serializers

from play_pi.models import *
from play_pi.utils import mpd_client


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
    playlist = serializers.IntegerField(required=False)
    playlistlength = serializers.IntegerField(required=False)
    state = serializers.ChoiceField(required=False, choices=['play', 'stop', 'pause'])
    song = serializers.IntegerField(required=False)
    songid = serializers.IntegerField(required=False)
    nextsong = serializers.IntegerField(required=False)
    nextsongid = serializers.IntegerField(required=False)
    time = serializers.CharField(required=False)
    elapsed = serializers.CharField(required=False)
    duration = serializers.IntegerField(required=False)
    bitrate = serializers.IntegerField(required=False)
    xfade = serializers.IntegerField(required=False)
    mixrampdb = serializers.FloatField(required=False)
    audio = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

    def create(self, validated_data):
        with mpd_client() as client:
            for key, value in validated_data.items():
                if value is not None:
                    setter = getattr(client, key)
                    setter(value)

            return client.status()