import json
import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list import ListView

from play_pi.models import *
from play_pi.utils import get_client, mpd_play, get_gplay_url, mpd_play_radio, get_currently_playing_track

logger = logging.getLogger(__name__)


def home(request):
	if not GoogleCredentials.objects.enabled().exists():
		return render_to_response('error.html', context_instance=RequestContext(request))
	artists = Artist.objects.all().order_by('name')
	return render_to_response('index.html',
		{'list': artists, 'view':'artist'},
		context_instance=RequestContext(request))

def albums(request):
	albums = Album.objects.all().order_by('name')
	return render_to_response('index.html',
		{'list': albums, 'view':'album'},
		context_instance=RequestContext(request))

def artist(request,artist_id):
	artist = Artist.objects.get(id=artist_id)
	albums = Album.objects.filter(artist=artist)
	return render_to_response('index.html',
		{'list': albums, 'view':'album', 'artist': artist},
		context_instance=RequestContext(request))

def playlists(request):
	playlists = Playlist.objects.all()
	return render_to_response('index.html',
		{'list': playlists, 'view':'playlist'},
		context_instance=RequestContext(request))

def playlist(request,playlist_id):
	playlist = Playlist.objects.get(id=playlist_id)
	tracks = [pc.track for pc in PlaylistConnection.objects.filter(playlist=playlist)]
	return render_to_response('playlist.html',
		{'playlist': playlist, 'tracks': tracks, 'view': 'single_playlist'},
		context_instance=RequestContext(request))

def album(request,album_id):
	album = Album.objects.get(id=album_id)
	tracks = Track.objects.filter(album=album).order_by('track_no')
	return render_to_response('album.html',
		{'album': album, 'tracks': tracks, 'view': 'single_album'},
		context_instance=RequestContext(request))

def play_album(request,album_id):
	album = Album.objects.get(id=album_id)
	tracks = Track.objects.filter(album=album).order_by('track_no')
	mpd_play(tracks)
	return HttpResponseRedirect(reverse('album',args=[album.id,]))

def play_artist(request,artist_id):
	artist = Artist.objects.get(id=artist_id)
	tracks = Track.objects.filter(artist=artist)
	mpd_play(tracks)
	return HttpResponseRedirect(reverse('artist',args=[artist.id,]))

def play_playlist(request,playlist_id):
	playlist = Playlist.objects.get(id=playlist_id)
	tracks = [pc.track for pc in PlaylistConnection.objects.filter(playlist=playlist)]
	mpd_play(tracks)
	return HttpResponseRedirect(reverse('playlist',args=[playlist.id,]))

def get_stream(request,track_id):
	track = Track.objects.get(id=track_id)
	url = get_gplay_url(track.stream_id)
	return HttpResponseRedirect(url)

def play_track(request,track_id):
	track = Track.objects.get(id=track_id)
	mpd_play([track,])
	return HttpResponseRedirect(reverse('album',args=[track.album.id,]))


def play_radio(request, radio_id):
	station = RadioStation.objects.get(id=radio_id)
	mpd_play_radio(station)
	return HttpResponseRedirect(reverse('radios'))


def stop(request):
	client = get_client()
	try:
          client.clear()
        except:
          pass
	client.stop()
	return HttpResponseRedirect(reverse('home'))

def random(request):
	client = get_client()
	status = client.status()
	client.random( (-1 * int(status['random'])) + 1 )
	return HttpResponseRedirect(reverse('home'))

def repeat(request):
	client = get_client()
	status = client.status()
	client.repeat( (-1 * int(status['repeat'])) + 1 )
	logger.debug(status)
	return HttpResponseRedirect(reverse('home'))


def ajax(request, method, value=None):
	client = get_client()
	status = client.status()
	if method == 'random':
		client.random( (-1 * int(status['random'])) + 1 )
	elif method == 'repeat':
		client.repeat( (-1 * int(status['repeat'])) + 1 )
	elif method == 'stop':
		client.stop()
	elif method == 'pause':
		client.pause()
	elif method == 'play':
		client.play()
	elif method == 'next':
		client.next()
	elif method == 'previous':
		client.previous()
	elif method == 'volume':
		volume = int(value)
		client.setvol(volume)
	elif method == 'current_song':
		track = get_currently_playing_track()
		if isinstance(track, Track):
			data = {'title': track.name, 'album': track.album.name, 'artist': track.artist.name, 'state': client.status()['state']}
		elif isinstance(track, RadioStation):
			data = {'title': track.name, 'album': '', 'artist': '', 'state': client.status()['state']}
		else:
			data = {}
		return HttpResponse(json.dumps(data), 'application/javascript')

	return_data = client.status()
	return HttpResponse(json.dumps(return_data), 'application/javascript')

class RadioStationListView(ListView):
	model = RadioStation
	template_name = 'radio_list.html'
