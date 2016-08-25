from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from play_pi.api.serializers import *
from play_pi.utils import mpd_client


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


class MpdStatusViewSet(APIView):
    """
    Provides low-level communication with MPD service
    """
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def get(self, request):
        with mpd_client() as client:
            status = client.status()
        serializer = MpdStatusSerializer(instance=status)
        return Response(serializer.data)
