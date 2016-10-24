from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers
from api.views import *

api_router = routers.DefaultRouter()
api_router.register(r'tracks', TrackViewSet)
api_router.register(r'radio_stations', RadioViewSet)
api_router.register(r'albums', AlbumViewSet)
api_router.register(r'playlists', PlaylistViewSet)

api_urls = [
    url(r'^status/$', MpdStatusViewSet.as_view(), name='mpd_status'),
    url(r'^queue/(?P<position>\d+)/$', QueueView.as_view(), name='queue'),
    url(r'^queue/$', QueueView.as_view(), name='queue'),
    url(r'^play/(?P<content_type>tracks|radios)$', PlayView.as_view(), name='play'),
    url(r'^', include(api_router.urls)),
]

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(api_urls, namespace='api')),
]
