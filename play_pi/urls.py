from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from play_pi.api.views import *
from play_pi.views import *

admin.autodiscover()

api_router = routers.DefaultRouter()
api_router.register(r'tracks', TrackViewSet)
api_router.register(r'radio_stations', RadioViewSet)
api_router.register(r'albums', AlbumViewSet)
api_router.register(r'playlists', PlaylistViewSet)

api = [
	url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^mpd_status/$', MpdStatusViewSet.as_view()),
	url(r'^', include(api_router.urls)),
]

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
	url(r'^controls/(?P<action>random|repeat|stop)/$', ControlView.as_view(), name='control'),
	url(r'^get_stream/(?P<track_id>\d+)/$', StreamView.as_view(), name='get_stream'),
	url(r'^ajax/(?P<method>\w+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^ajax/(?P<method>\w+)/(?P<value>[\-\d]+)/?$', AjaxView.as_view(), name='ajax'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/', include(api)),
]
