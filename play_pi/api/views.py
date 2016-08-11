from __future__ import unicode_literals

from rest_framework import viewsets

from play_pi import models
from play_pi.api.serializers import *


class TrackViewSet(viewsets.ModelViewSet):
    queryset = models.Track.objects.all()
    serializer_class = TrackSerializer


class RadioViewSet(viewsets.ModelViewSet):
    queryset = models.RadioStation.objects.all()
    serializer_class = RadioSerializer
