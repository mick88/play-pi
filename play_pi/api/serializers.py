from __future__ import unicode_literals
from rest_framework import serializers

from play_pi.models import *


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
    repeat = serializers.BooleanField(required=False)
    random = serializers.BooleanField(required=False)
    single = serializers.BooleanField(required=False)
    consume = serializers.BooleanField(required=False)
    playlist = serializers.IntegerField(required=False)
    playlistlength = serializers.IntegerField(required=False)
    state = serializers.CharField(required=False)
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
