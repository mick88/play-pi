from __future__ import unicode_literals

import mpd
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APITestCase

from api.tests.mock_mpd import MockMpdClient
from play_pi.models import Track, RadioStation


class TestJumpApi(APITestCase):
    @classmethod
    def setUpClass(cls):
        super(TestJumpApi, cls).setUpClass()
        # Use mock MPD client
        mpd.MPDClient = MockMpdClient

    @classmethod
    def setUpTestData(cls):
        super(TestJumpApi, cls).setUpTestData()
        cls.track1 = mommy.make(Track, mpd_id=14)
        cls.track2 = mommy.make(Track, mpd_id=15)
        cls.radio = mommy.make(RadioStation, mpd_id=16)

    def setUp(self):
        super(TestJumpApi, self).setUp()
        MockMpdClient.PLAYLIST = [
            {'pos': '0', 'file': 'http://localhost:8000/get_stream/2002/', 'id': '14'},
            {'pos': '1', 'file': 'http://localhost:8000/get_stream/1970/', 'id': '15'},
            {'pos': '2', 'file': 'http://localhost:8000/get_stream/1640/', 'id': '16'},
        ]
        MockMpdClient.status_data['song'] = 0
        self.user = get_user_model().objects.create_user('test_user')
        self.client.force_login(self.user)

    def tearDown(self):
        super(TestJumpApi, self).tearDown()
        MockMpdClient.instance = None

    def test_jump_track(self):
        url = reverse('api:jump', kwargs=dict(to='track'))
        data = {
            'id': self.track2.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, MockMpdClient.instance.status_data['song'])
        self.assertEqual(15, response.data['track']['mpd_id'])

    def test_jump_radio(self):
        url = reverse('api:jump', kwargs=dict(to='radio'))
        data = {
            'id': self.radio.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, MockMpdClient.instance.status_data['song'])
        self.assertEqual(16, response.data['radio_station']['mpd_id'])

    def test_jump_next(self):
        url = reverse('api:jump', kwargs=dict(to='next'))

        response = self.client.post(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, MockMpdClient.instance.status_data['song'])
        self.assertEqual(15, response.data['track']['mpd_id'])


    def test_jump_previous(self):
        MockMpdClient.status_data['song'] = 1
        url = reverse('api:jump', kwargs=dict(to='previous'))

        response = self.client.post(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, MockMpdClient.instance.status_data['song'])
        self.assertEqual(14, response.data['track']['mpd_id'])
