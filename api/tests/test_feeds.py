from __future__ import unicode_literals

from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APITestCase

from play_pi.models import Track, RadioStation, Playlist, Album


class FeedTest(APITestCase):
    def test_tracks_api(self):
        url = reverse('api:track-list')

        mommy.make(Track, name='Test track')

        response = self.client.get(url)
        self.assertContains(response, 'Test track')

    def test_radio_api(self):
        url = reverse('api:radiostation-list')

        mommy.make(RadioStation, name='Test station')

        response = self.client.get(url)
        self.assertContains(response, 'Test station')


    def test_playlist_api(self):
        url = reverse('api:playlist-list')

        mommy.make(Playlist, name='Test playlist')

        response = self.client.get(url)
        self.assertContains(response, 'Test playlist')


    def test_album_api(self):
        url = reverse('api:album-list')

        mommy.make(Album, name='Test album')

        response = self.client.get(url)
        self.assertContains(response, 'Test album')
