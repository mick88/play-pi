from django.conf.urls import patterns, include, url
from django.contrib import admin

from play_pi.models import *
from play_pi.views import RadioStationListView, AjaxView, ArtistListView, AlbumListView, PlaylistListView, ArtistView, \
	PlaylistView, AlbumView, PlayView, StreamView, ControlView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', ArtistListView.as_view(), name='home'),
	url(r'^albums/$', AlbumListView.as_view(), name='albums'),
	url(r'^artist/(?P<artist_id>\d+)/$', ArtistView.as_view(), name='artist'),
	url(r'^album/(?P<album_id>\d+)/$', AlbumView.as_view(), name='album'),
	url(r'^radio/$', RadioStationListView.as_view(), name='radios'),
	url(r'^playlists/$', PlaylistListView.as_view(), name='playlists'),
	url(r'^playlist/(?P<playlist_id>\d+)/$', PlaylistView.as_view(), name='playlist'),
	url(r'^play/(?P<entity>track|radio|album|artist|playlist)/(?P<play_id>\d+)/$', PlayView.as_view(), name='play'),
	url(r'^controls/(?P<action>random|repeat|stop)/$', ControlView.as_view(), name='control'),
	url(r'^get_stream/(?P<track_id>\d+)/$', StreamView.as_view(), name='get_stream'),
	url(r'^ajax/(?P<method>\w+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^ajax/(?P<method>volume)/(?P<value>\d+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^admin/', include(admin.site.urls)),
)
