from rest_framework import serializers

from play_pi import models


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = '__all__'


class RadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RadioStation
        fields = '__all__'
