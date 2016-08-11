from __future__ import unicode_literals

from rest_framework import viewsets

from play_pi.api.serializers import *


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.select_related('artist', 'album__artist')
    serializer_class = TrackSerializer


class RadioViewSet(viewsets.ModelViewSet):
    queryset = RadioStation.objects.all()
    serializer_class = RadioSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.prefetch_related('tracks__artist', 'tracks__album__artist')
    serializer_class = PlaylistSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related('artist')
    serializer_class = AlbumSerializer
