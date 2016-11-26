import logging

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from play_pi.forms import SearchForm
from play_pi.models import *
from play_pi.utils import mpd_play, get_gplay_url, mpd_play_radio, mpd_client, mpd_enqueue
from play_pi.views.mixins import CacheMixin

logger = logging.getLogger(__name__)


class BaseGridView(ListView):
    ordering = 'name',
    context_object_name = 'list'
    template_name = 'grid.html'


class TrackListView(CacheMixin, ListView):
    queryset = Track.objects.all().select_related('artist')
    template_name = 'track_list.html'
    paginate_by = 50
    ordering = (
        'artist__name',
        'name',
    )
    tab = 'tracks'

    @property
    def pagination_extras(self):
        extra = u''
        if self.search_form.is_valid():
            for field, value in self.search_form.cleaned_data.items():
                extra += u'{field}={value}&'.format(field=field, value=value)
        return extra

    @cached_property
    def search_form(self):
        data = self.request.GET if 'q' in self.request.GET else None
        return SearchForm(data=data)

    def get_queryset(self):
        qs = super(TrackListView, self).get_queryset()
        if self.search_form.is_valid():
            qs = self.search_form.filter(qs)
        return qs


class QueueView(TemplateView):
    template_name = 'queue.html'
    tab = 'queue'

    def get_context_data(self, **kwargs):
        data = super(QueueView, self).get_context_data(**kwargs)
        try:
            with mpd_client() as client:
                playlist = client.playlistinfo()
                status = client.status()

            current_id = int(status.get('songid', 0)) or None
            ids = [int(song['id']) for song in playlist]
            tracks = list(Track.objects.filter(mpd_id__in=ids).select_related('artist'))
            radios = list(RadioStation.objects.filter(mpd_id__in=ids))
            tracks = sorted(tracks + radios, key=lambda track: ids.index(track.mpd_id))
            data['tracks'] = tracks
            data['current_track'] = next((track for track in tracks if track.mpd_id == current_id), None)
        except Exception as e:
            error_message = u'Could not connect to MPD service: {}'.format(e)
            logger.error(error_message)
            messages.error(self.request, error_message)
        return data


class ArtistListView(CacheMixin, BaseGridView):
    model = Artist
    tab = 'artists'


class AlbumListView(CacheMixin, BaseGridView):
    model = Album
    tab = 'albums'


class ArtistView(CacheMixin, DetailView):
    pk_url_kwarg = 'artist_id'
    model = Artist
    template_name = 'grid.html'
    tab = 'artists'

    def get_context_data(self, **kwargs):
        data = super(ArtistView, self).get_context_data(**kwargs)
        data['list'] = Album.objects.filter(artist=self.object)
        return data


class PlaylistListView(CacheMixin, BaseGridView):
    model = Playlist
    tab = 'playlists'


class PlaylistView(CacheMixin, DetailView):
    model = Playlist
    pk_url_kwarg = 'playlist_id'
    template_name = 'playlist.html'
    context_object_name = 'playlist'
    tab = 'playlists'

    def get_context_data(self, **kwargs):
        data = super(PlaylistView, self).get_context_data(**kwargs)
        data['tracks'] = self.object.tracks.select_related('artist')
        return data


class AlbumView(CacheMixin, DetailView):
    model = Album
    pk_url_kwarg = 'album_id'
    template_name = 'album.html'
    tab = 'albums'

    def get_context_data(self, **kwargs):
        data = super(AlbumView, self).get_context_data(**kwargs)
        data['tracks'] = Track.objects.filter(album=self.object).order_by('track_no')
        return data


class PlayView(View):
    def play_album(self, album_id):
        album = Album.objects.get(id=album_id)
        tracks = Track.objects.filter(album=album).order_by('track_no')
        mpd_play(tracks)
        return HttpResponseRedirect(reverse('album', args=[album.id, ]))

    def play_artist(self, artist_id):
        artist = Artist.objects.get(id=artist_id)
        tracks = Track.objects.filter(artist=artist)
        mpd_play(tracks)
        return HttpResponseRedirect(reverse('artist', args=[artist.id, ]))

    def play_playlist(self, playlist_id):
        playlist = Playlist.objects.get(id=playlist_id)
        tracks = [pc.track for pc in PlaylistConnection.objects.filter(playlist=playlist)]
        mpd_play(tracks)
        return HttpResponseRedirect(reverse('playlist', args=[playlist.id, ]))

    def play_track(self, track_id):
        track = Track.objects.get(id=track_id)
        mpd_play([track, ])
        url = self.request.META.get('HTTP_REFERER', reverse_lazy('queue'))
        return HttpResponseRedirect(url)

    def play_jump(self, mpd_id):
        with mpd_client() as client:
            client.playid(mpd_id)
        return HttpResponseRedirect(reverse('queue'))

    def play_track_enqueue(self, track_id):
        track = Track.objects.get(id=track_id)
        mpd_enqueue(track)
        url = self.request.META.get('HTTP_REFERER', reverse_lazy('queue'))
        return HttpResponseRedirect(url)

    def play_radio_enqueue(self, radio_id):
        station = RadioStation.objects.get(id=radio_id)
        mpd_enqueue(station)
        url = self.request.META.get('HTTP_REFERER', reverse_lazy('queue'))
        return HttpResponseRedirect(url)

    def play_radio(self, radio_id):
        station = RadioStation.objects.get(id=radio_id)
        mpd_play_radio(station)
        return HttpResponseRedirect(reverse('radios'))

    def dispatch(self, request, *args, **kwargs):
        entity = kwargs.get('entity')
        play_id = kwargs.get('play_id')
        play = getattr(self, 'play_{}'.format(entity))
        if play is None:
            raise Http404('Play {} not available'.format(entity))
        return play(play_id)


class StreamView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        track = get_object_or_404(Track, id=kwargs['track_id'])
        return get_gplay_url(track.stream_id)


class RadioStationListView(CacheMixin, ListView):
    model = RadioStation
    template_name = 'radio_list.html'
    tab = 'radios'
