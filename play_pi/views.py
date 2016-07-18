import json
import logging

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.http.response import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.views.generic.base import RedirectView
from play_pi.models import *
from play_pi.utils import get_client, mpd_play, get_gplay_url, mpd_play_radio, get_currently_playing_track

logger = logging.getLogger(__name__)


class BaseGridView(ListView):
	ordering = 'name',
	context_object_name = 'list'
	template_name = 'grid.html'

	def dispatch(self, request, *args, **kwargs):
		if not GoogleCredentials.objects.enabled().exists():
			return render_to_response('error.html', context_instance=RequestContext(request))
		return super(BaseGridView, self).dispatch(request, *args, **kwargs)


class ArtistListView(BaseGridView):
	model = Artist


class AlbumListView(BaseGridView):
	model = Album


class ArtistView(DetailView):
	pk_url_kwarg = 'artist_id'
	model = Artist
	template_name = 'grid.html'

	def get_context_data(self, **kwargs):
		data = super(ArtistView, self).get_context_data(**kwargs)
		data['list'] = Album.objects.filter(artist=self.object)
		data['view'] = 'album'
		return data


class PlaylistListView(BaseGridView):
	model = Playlist


class PlaylistView(DetailView):
	model = Playlist
	pk_url_kwarg = 'playlist_id'
	template_name = 'playlist.html'
	context_object_name = 'playlist'

	def get_context_data(self, **kwargs):
		data = super(PlaylistView, self).get_context_data(**kwargs)
		data['tracks'] = [pc.track for pc in PlaylistConnection.objects.filter(playlist=self.object)]
		data['view'] = 'single_playlist'
		return data


class AlbumView(DetailView):
	model = Album
	pk_url_kwarg = 'album_id'
	template_name = 'album.html'

	def get_context_data(self, **kwargs):
		data = super(AlbumView, self).get_context_data(**kwargs)
		data['tracks'] = Track.objects.filter(album=self.object).order_by('track_no')
		data['view'] = 'single_album'
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
		return HttpResponseRedirect(reverse('album', args=[track.album.id, ]))

	def play_radio(self, radio_id):
		station = RadioStation.objects.get(id=radio_id)
		mpd_play_radio(station)
		return HttpResponseRedirect(reverse('radios'))

	def dispatch(self, request, *args, **kwargs):
		entity = kwargs.get('entity')
		play_id = kwargs.get('play_id')
		play = getattr(self, 'play_{}'.format(entity))
		return play(play_id)


class StreamView(RedirectView):
	def get_redirect_url(self, *args, **kwargs):
		track = get_object_or_404(Track, id=kwargs['track_id'])
		return get_gplay_url(track.stream_id)


class ControlView(RedirectView):
	url = reverse_lazy('home')

	def control_stop(self):
		client = get_client()
		try:
			client.clear()
		except:
			pass
		client.stop()

	def control_random(self):
		client = get_client()
		status = client.status()
		client.random((-1 * int(status['random'])) + 1)

	def control_repeat(self):
		client = get_client()
		status = client.status()
		client.repeat((-1 * int(status['repeat'])) + 1)
		logger.debug(status)

	def dispatch(self, request, *args, **kwargs):
		action = kwargs['action']
		control = getattr(self, 'control_{}'.format(action))
		control()
		return super(ControlView, self).dispatch(request, *args, **kwargs)


class AjaxView(View):
	def ajax_random(self, client, *args, **kwargs):
		status = client.status()
		client.random((-1 * int(status['random'])) + 1)
		return client.status()

	def ajax_repeat(self, client, *args, **kwargs):
		status = client.status()
		client.repeat((-1 * int(status['repeat'])) + 1)
		return client.status()

	def ajax_stop(self, client, *args, **kwargs):
		client.stop()
		return client.status()

	def ajax_pause(self, client, *args, **kwargs):
		client.pause()
		return client.status()

	def ajax_play(self, client, *args, **kwargs):
		client.play()
		return client.status()

	def ajax_next(self, client, *args, **kwargs):
		client.next()
		return client.status()

	def ajax_previous(self, client, *args, **kwargs):
		client.previous()
		return client.status()

	def ajax_volume(self, client, value, *args, **kwargs):
		volume = int(value)
		client.setvol(volume)
		return client.status()

	def ajax_current_song(self, client, *args, **kwargs):
		try:
			track = get_currently_playing_track()
			if isinstance(track, Track):
				return {
					'title': track.name,
					'album': track.album.name,
					'artist': track.artist.name,
					'state': client.status()['state'],
				}
			elif isinstance(track, RadioStation):
				return {
					'title': track.name,
					'album': '',
					'artist': '',
					'state': client.status()['state'],
				}
			else:
				return {}
		except Exception as e:
			logger.error(e.message)
			return {}

	def dispatch(self, request, *args, **kwargs):
		method = getattr(self, u'ajax_{method}'.format(**kwargs), None)
		if method is None:
			raise Http404(u'Method {method} does not exist'.format(**kwargs))
		client = get_client()
		data = method(client, *args, **kwargs)
		return HttpResponse(json.dumps(data), 'application/javascript')


class RadioStationListView(ListView):
	model = RadioStation
	template_name = 'radio_list.html'
