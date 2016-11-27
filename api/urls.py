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
    url(r'^status/$', MpdStatusAPIView.as_view(), name='mpd_status'),
    url(r'^queue/(?P<position>\d+)/$', QueueAPIViewCombined.as_view(), name='queue'),
    url(r'^queue/$', QueueAPIViewCombined.as_view(), name='queue'),
    url(r'^queue/items$', QueueAPIView.as_view(), name='queue-items'),
    url(r'^queue/current$', NowPlayingApiView.as_view(), name='now-playing'),
    url(r'^play/(?P<content_type>tracks|radios)$', PlayAPIView.as_view(), name='play'),
    url(r'^jump/(?P<to>track|radio|next|previous)$', JumpAPIView.as_view(), name='jump'),
    url(r'^', include(api_router.urls)),
]

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(api_urls, namespace='api')),
]
