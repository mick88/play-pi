from __future__ import unicode_literals

from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from validate import ValidateError

from api.serializers import *
from play_pi import utils
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

    def get(self, request, position=None):
        with mpd_client() as client:
            return self.render_queue(client)

    def post(self, request, position=None):
        serializer = QueueItemSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            with mpd_client() as client:
                if position is not None:
                    position = int(position)
                serializer.enqueue(client, position)
            return self.render_queue(client)
        else:
            return Response(serializer.errors, status=401)

    def delete(self, request, position=None):
        """
        Delete = clear queue / remove track
        position arg is used as mpd_id in this case
        """
        with mpd_client() as client:
            if position is None:
                client.clear()
            else:
                client.deleteid(position)
            return self.render_queue(client)


class PlayView(APIView):
    """
    POST to this endpoint to clear queue and start playing new items.
    /api/play/tracks - POST list of Tracks
    /api/play/radios - POST list of RadioStations
    The current playlist will be cleared, populated with posted items, and played
    """
    http_method_names = 'post',
    permission_classes = [
        IsAuthenticated,
    ]

    def play(self, items):
        with mpd_client() as client:
            client.clear()
            utils.mpd_client_enqueue(client, *items)
            client.play()

    def post(self, request, content_type):
        if content_type not in ('tracks', 'radios'):
            raise ValidateError('Content type {content_type} is not supported by this API.'.format(
                content_type=content_type,
            ))
        if content_type == 'tracks':
            model = Track
            serializer_class = TrackSerializer
        else:
            model = RadioStation
            serializer_class = RadioSerializer
        serializer = serializer_class(data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)
        ids = tuple(item['id'] for item in request.data)
        items = model.objects.filter(pk__in=ids).order_by()
        # order items in the same order as POSTed
        items = sorted(items, key=lambda item: ids.index(item.id))
        self.play(items)
        serializer = serializer_class(instance=items, many=True)
        return Response(data=serializer.data)


class JumpView(APIView):
    """
    POST to this endpoint to jump to an item in the queue
    /api/jump/track - post Track instance to jump to the track
    /api/jump/radio - post Radio station instance to jump to the radio
    /api/jump/next - jump to the next item relative to current
    /api/jump/previous - jump to previous item relative to current
    """
    http_method_names = 'post',
    permission_classes = [
        IsAuthenticated,
    ]

    def jump_to(self, item):
        """
        Jump to item in the queue
        Args:
            item: Track or Radio instance, or string "next" or "previous"
        """
        with mpd_client() as client:
            if item in ('next', 'previous'):
                method = getattr(client, item)
                return method()
            else:
                return client.playid(item.mpd_id)

    def post(self, request, to):
        if to.startswith('track'):
            model = Track
            serializer_class = TrackSerializer
        elif to.startswith('radio'):
            model = RadioStation
            serializer_class = RadioSerializer
        else:
            model = None
            serializer_class = None

        if model is None:
            # Jumping to next/previous item
            self.jump_to(to)
            item = utils.get_currently_playing_track()
        else:
            serializer = serializer_class(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            pk = request.data['id']
            item = get_object_or_404(model, pk=pk)
            if not item.mpd_id:
                raise Http404('{} not found in the queue'.format(item))
            self.jump_to(item)

        if item:
            serializer = QueueItemSerializer(instance={
                'mpd_id': item.mpd_id,
                'track' if isinstance(item, Track) else 'radio_station': item,
            })
        else:
            serializer = QueueItemSerializer(instance=None)
        return Response(data=serializer.data)
