from gmusicapi import Mobileclient
import mpd
from django.core.cache import cache

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.shortcuts import render_to_response
from django.template import RequestContext
import json

from play_pi.models import *
from play_pi.settings import GPLAY_USER, GPLAY_PASS, SITE_ROOT, DEVICE_ID

import logging
logger = logging.getLogger('play_pi')

api = Mobileclient()
api.login(GPLAY_USER,GPLAY_PASS,DEVICE_ID)

client = mpd.MPDClient()
client.connect("localhost", 6600)

def home(request):
	if GPLAY_USER == "" or GPLAY_PASS == "":
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
		if track == {}:
			return HttpResponse(json.dumps({}), 'application/javascript')
		data = {'title': track.name, 'album':track.album.name, 'artist': track.artist.name, 'state': client.status()['state']}
		return HttpResponse(json.dumps(data), 'application/javascript')
	
	return_data = client.status()
	return HttpResponse(json.dumps(return_data), 'application/javascript')

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
	except MultipleObjectsReturned:
		return {}

def get_gplay_url(stream_id):
	global api
        try:
	  url = api.get_stream_url(stream_id,DEVICE_ID)
        except:
          api.login(GPLAY_USER,GPLAY_PASS,DEVICE_ID)
          url = api.get_stream_url(stream_id,DEVICE_ID)
	return url

def mpd_play(tracks):
	client = get_client()
        success = False
        while not success:
          try:
            client.clear()
            for track in tracks:
              track.mpd_id = client.addid(SITE_ROOT + reverse('get_stream',args=[track.id,]))
              track.save()
            client.play()
            success = True
          except:
            pass

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
