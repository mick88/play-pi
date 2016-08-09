from __future__ import unicode_literals
from rest_framework import routers, serializers, viewsets

from play_pi import models


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = '__all__'


class TrackViewSet(viewsets.ModelViewSet):
    queryset = models.Track.objects.all()
    serializer_class = TrackSerializer


class RadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RadioStation
        fields = '__all__'


class RadioViewSet(viewsets.ModelViewSet):
    queryset = models.RadioStation.objects.all()
    serializer_class = RadioSerializer
