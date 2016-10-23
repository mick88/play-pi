from __future__ import unicode_literals

import mpd
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.mock_mpd import MockMpdClient


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
