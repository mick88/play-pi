import json
import logging

import mpd
from django.apps import apps
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list import ListView

from play_pi.models import *

logger = logging.getLogger('play_pi')

client = mpd.MPDClient()
client.connect("localhost", 6600)

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

def ajax(request,method):
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

def get_currently_playing_track():
	status = get_client().status()
	try:
		mpd_id = int(status['songid'])
	except:
		return {}

	if mpd_id == 0:
		 return {}

	try:
		track = Track.objects.get(mpd_id=mpd_id)
		return track
	except Track.DoesNotExist:
		return RadioStation.objects.get(mpd_id=mpd_id)
	except MultipleObjectsReturned:
		return {}

def get_gplay_url(stream_id):
	app = apps.get_app_config('play_pi')
	api = app.get_api()
	return api.get_stream_url(stream_id, app.get_credentials().device_id)

def mpd_play(tracks):
	client = get_client()
        success = False
        while not success:
          try:
            client.clear()
            for track in tracks:
				site = Site.objects.get_current()
				track.mpd_id = client.addid(site.domain + reverse('get_stream',args=[track.id,]))
				track.save()
            client.play()
            success = True
          except:
            pass

def mpd_play_radio(station):
	client = get_client()
	client.clear()
	mpd_id = client.addid(station.url)
	station.mpd_id = mpd_id
	station.save()
	client.play()

def get_client():
	global client
	try:
		client.status()
	except:
		try:
			client.connect("localhost", 6600)
		except Exception, e:
			logger.error(e.message)
	return client
