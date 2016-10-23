from __future__ import unicode_literals

import mpd
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.mock_mpd import MockMpdClient


class TestStatusApi(APITestCase):
    url = reverse('api:mpd_status')

    @classmethod
    def setUpClass(cls):
        super(TestStatusApi, cls).setUpClass()
        # Use mock MPD client
        mpd.MPDClient = MockMpdClient

    def setUp(self):
        super(TestStatusApi, self).setUp()
        self.user = get_user_model().objects.create_user('test_user')
        self.client.force_login(self.user)

    def test_status_get(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        data = response.data

        self.assertEqual('play', data['state'])

    def test_update_state(self):
        data = {
            'state': 'pause',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        data = response.data
        self.assertEqual('pause', data['state'])

    def test_update_volume(self):
        data = {
            'volume': '100',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        data = response.data
        self.assertEqual(100, int(data['volume']))


    def test_update_repeat_true(self):
        data = {
            'repeat': True,
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        data = response.data
        self.assertEqual(True, bool(data['repeat']))

    def test_update_repeat_false(self):
        data = {
            'repeat': False,
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(200, response.status_code)
        data = response.data
        self.assertEqual(False, bool(data['repeat']))
