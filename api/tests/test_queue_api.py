from __future__ import unicode_literals

import mpd
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APITestCase

from api.tests.mock_mpd import MockMpdClient
from play_pi.models import Track, RadioStation


class TestQueueApi(APITestCase):
    url = reverse('api:queue')

    @classmethod
    def setUpClass(cls):
        super(TestQueueApi, cls).setUpClass()
        # Use mock MPD client
        mpd.MPDClient = MockMpdClient

    def setUp(self):
        super(TestQueueApi, self).setUp()
        self.user = get_user_model().objects.create_user('test_user')
        self.client.force_login(self.user)

    def test_get_queue(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_enqueue_track(self):
        track = mommy.make(Track)

        MockMpdClient.PLAYLIST = []
        self.assertFalse(MockMpdClient.PLAYLIST)
        data = {
            'track': {
                'id': track.id,
            },
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(MockMpdClient.PLAYLIST))

    def test_enqueue_radio(self):
        radio_station = mommy.make(RadioStation)

        MockMpdClient.PLAYLIST = []
        self.assertFalse(MockMpdClient.PLAYLIST)
        data = {
            'radio_station': {
                'id': radio_station.id,
            },
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(MockMpdClient.PLAYLIST))
