from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers
from api.views import *

api_router = routers.DefaultRouter()
api_router.register(r'tracks', TrackViewSet)
api_router.register(r'radio_stations', RadioViewSet)
api_router.register(r'albums', AlbumViewSet)
api_router.register(r'playlists', PlaylistViewSet)

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^mpd_status/$', MpdStatusViewSet.as_view()),
    url(r'^', include(api_router.urls)),
]
