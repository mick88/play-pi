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
