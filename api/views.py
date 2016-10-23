from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import *
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
    Provides low-level communication with MPD service.
    POST to this endpoint to update values with any non-null fields.
    More information: https://pythonhosted.org/python-mpd2/topics/commands.html#MPDClient.status
    """
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def render_status_json_response(self, status):
        """
        renders status json response
        """
        serializer = MpdStatusSerializer(instance=status)
        return Response(serializer.data)

    def get(self, request):
        with mpd_client() as client:
            return self.render_status_json_response(client.status())

    def post(self, request):
        serializer = MpdStatusSerializer(data=request.data)
        if serializer.is_valid():
            status = serializer.save()
            return self.render_status_json_response(status)
        else:
            return Response(serializer.data)


class QueueView(APIView):
    """
    Endpoint for managing API queue.
    POSTing queue items to this url adds them to the queue.
    """
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def render_queue(self, client):
        playlist = client.playlistinfo()
        ids = tuple(int(song['id']) for song in playlist)
        tracks = list(Track.objects.filter(mpd_id__in=ids).select_related('artist'))
        radios = list(RadioStation.objects.filter(mpd_id__in=ids))
        items = sorted(tracks + radios, key=lambda track: ids.index(track.mpd_id))
        items = [{
                     'mpd_id': item.mpd_id,
                     'track' if isinstance(item, Track) else 'radio_station': item,
                 } for item in items]
        serializer = QueueItemSerializer(many=True, instance=items)
        return Response(serializer.data)

    def get(self, request):
        with mpd_client() as client:
            return self.render_queue(client)

    def post(self, request):
        serializer = QueueItemSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            with mpd_client() as client:
                serializer.enqueue(client)
            return self.render_queue(client)
        else:
            return Response(serializer.errors, status=401)

    def delete(self, request):
        """Delete = clear queue"""
        with mpd_client() as client:
            client.clear()
            return self.render_queue(client)
