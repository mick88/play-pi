from django.conf.urls import patterns, include, url
from django.contrib import admin

from play_pi.models import *
from play_pi.views import RadioStationListView, AjaxView, ArtistListView, AlbumListView, PlaylistListView, ArtistView, \
	PlaylistView, AlbumView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', ArtistListView.as_view(), name='home'),
	url(r'^albums/$', AlbumListView.as_view(), name='albums'),
	url(r'^artist/(?P<artist_id>\d+)/$', ArtistView.as_view(), name='artist'),
	url(r'^album/(?P<album_id>\d+)/$', AlbumView.as_view(), name='album'),
	url(r'^radio/$', RadioStationListView.as_view(), name='radios'),
	url(r'^playlists/$', PlaylistListView.as_view(), name='playlists'),
	url(r'^playlist/(?P<playlist_id>\d+)/$', PlaylistView.as_view(), name='playlist'),
	url(r'^play/track/(?P<track_id>\d+)/$', 'play_pi.views.play_track', name='play_track'),
	url(r'^play/radio/(?P<radio_id>\d+)/$', 'play_pi.views.play_radio', name='play_radio'),
	url(r'^play/album/(?P<album_id>\d+)/$', 'play_pi.views.play_album', name='play_album'),
	url(r'^play/artist/(?P<artist_id>\d+)/$', 'play_pi.views.play_artist', name='play_artist'),
	url(r'^play/playlist/(?P<playlist_id>\d+)/$', 'play_pi.views.play_playlist', name='play_playlist'),
	url(r'^controls/random/$', 'play_pi.views.random', name='random'),
	url(r'^controls/repeat/$', 'play_pi.views.repeat', name='repeat'),
	url(r'^get_stream/(?P<track_id>\d+)/$', 'play_pi.views.get_stream', name='get_stream'),
	url(r'^stop/$', 'play_pi.views.stop', name='stop'),
	url(r'^ajax/(?P<method>\w+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^ajax/(?P<method>volume)/(?P<value>\d+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^admin/', include(admin.site.urls)),
)
