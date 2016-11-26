from django.conf.urls import include, url
from django.contrib import admin

from api.views import *
from play_pi.views.views import *

admin.autodiscover()

urlpatterns = [
	url(r'^$', QueueView.as_view(), name='home'),
	url(r'^albums/$', AlbumListView.as_view(), name='albums'),
	url(r'^tracks/$', TrackListView.as_view(), name='tracks'),
	url(r'^artists/$', ArtistListView.as_view(), name='artists'),
	url(r'^artist/(?P<artist_id>\d+)/$', ArtistView.as_view(), name='artist'),
	url(r'^album/(?P<album_id>\d+)/$', AlbumView.as_view(), name='album'),
	url(r'^radio/$', RadioStationListView.as_view(), name='radios'),
	url(r'^queue/$', QueueView.as_view(), name='queue'),
	url(r'^playlists/$', PlaylistListView.as_view(), name='playlists'),
	url(r'^playlist/(?P<playlist_id>\d+)/$', PlaylistView.as_view(), name='playlist'),
	url(r'^play/(?P<entity>\w+)/(?P<play_id>\d+)/$', PlayView.as_view(), name='play'),
	url(r'^get_stream/(?P<track_id>\d+)/$', StreamView.as_view(), name='get_stream'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include('api.urls')),
]
