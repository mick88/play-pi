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
        MockMpdClient.PLAYLIST = [{'pos': '0', 'file': 'http://localhost:8000/get_stream/2002/', 'id': '14'}, {'pos': '1', 'file': 'http://localhost:8000/get_stream/1970/', 'id': '15'}, {'pos': '2', 'file': 'http://localhost:8000/get_stream/1640/', 'id': '16'}, {'pos': '3', 'file': 'http://localhost:8000/get_stream/1736/', 'id': '17'}, {'pos': '4', 'file': 'http://localhost:8000/get_stream/1895/', 'id': '18'}, {'pos': '5', 'file': 'http://localhost:8000/get_stream/1955/', 'id': '19'}, {'pos': '6', 'file': 'http://localhost:8000/get_stream/1744/', 'id': '20'}, {'pos': '7', 'file': 'http://localhost:8000/get_stream/1828/', 'id': '21'}, {'pos': '8', 'file': 'http://localhost:8000/get_stream/1366/', 'id': '22'}, {'pos': '9', 'file': 'http://localhost:8000/get_stream/1425/', 'id': '23'}, {'pos': '10', 'file': 'http://localhost:8000/get_stream/2001/', 'id': '24'}, {'pos': '11', 'file': 'http://localhost:8000/get_stream/1389/', 'id': '25'}, {'pos': '12', 'file': 'http://localhost:8000/get_stream/1973/', 'id': '26'}, {'pos': '13', 'file': 'http://localhost:8000/get_stream/1575/', 'id': '27'}, {'pos': '14', 'file': 'http://localhost:8000/get_stream/1971/', 'id': '28'}, {'pos': '15', 'file': 'http://localhost:8000/get_stream/1333/', 'id': '29'}, {'pos': '16', 'file': 'http://localhost:8000/get_stream/1248/', 'id': '30'}, {'pos': '17', 'file': 'http://localhost:8000/get_stream/1865/', 'id': '31'}, {'pos': '18', 'file': 'http://localhost:8000/get_stream/1962/', 'id': '32'}, {'pos': '19', 'file': 'http://localhost:8000/get_stream/2005/', 'id': '33'}, {'pos': '20', 'file': 'http://localhost:8000/get_stream/1508/', 'id': '34'}, {'pos': '21', 'file': 'http://localhost:8000/get_stream/2013/', 'id': '35'}, {'pos': '22', 'file': 'http://localhost:8000/get_stream/1777/', 'id': '36'}, {'pos': '23', 'file': 'http://localhost:8000/get_stream/1799/', 'id': '37'}, {'pos': '24', 'file': 'http://localhost:8000/get_stream/1526/', 'id': '38'}, {'pos': '25', 'file': 'http://localhost:8000/get_stream/1776/', 'id': '39'}, {'pos': '26', 'file': 'http://localhost:8000/get_stream/1979/', 'id': '40'}, {'pos': '27', 'file': 'http://localhost:8000/get_stream/1956/', 'id': '41'}, {'pos': '28', 'file': 'http://localhost:8000/get_stream/2010/', 'id': '42'}, {'pos': '29', 'file': 'http://localhost:8000/get_stream/1334/', 'id': '43'}, {'pos': '30', 'file': 'http://localhost:8000/get_stream/1335/', 'id': '44'}, {'pos': '31', 'file': 'http://localhost:8000/get_stream/1995/', 'id': '45'}, {'pos': '32', 'file': 'http://localhost:8000/get_stream/1836/', 'id': '46'}, {'pos': '33', 'file': 'http://localhost:8000/get_stream/1718/', 'id': '47'}, {'pos': '34', 'file': 'http://localhost:8000/get_stream/1994/', 'id': '48'}]
        self.user = get_user_model().objects.create_user('test_user')
        self.client.force_login(self.user)

    def test_get_queue(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_enqueue_track(self):
        track = mommy.make(Track)
        self.assertFalse(track.mpd_id)

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
        track = Track.objects.get(pk=track.pk)
        self.assertTrue(track.mpd_id)

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

    def test_delete_queue(self):
        self.assertTrue(MockMpdClient.PLAYLIST)

        response = self.client.delete(self.url)
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, len(MockMpdClient.PLAYLIST))

    def test_delete_track(self):
        track = {'pos': '0', 'file': 'http://localhost:8000/get_stream/2002/', 'id': '144'}
        MockMpdClient.PLAYLIST.append(track)
        self.assertTrue(track in MockMpdClient.PLAYLIST)

        url = reverse('api:queue', kwargs={'position': 144})
        response = self.client.delete(url)
        self.assertEqual(200, response.status_code)

        self.assertFalse(track in MockMpdClient.PLAYLIST)

    def test_track_insert(self):
        track = mommy.make(Track)
        self.assertFalse(track.mpd_id)
        self.assertTrue(MockMpdClient.PLAYLIST)

        data = {
            'track': {
                'id': track.id,
            },
        }

        self.assertTrue(MockMpdClient.PLAYLIST)
        url = reverse('api:queue', kwargs={'position': 0})
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        track = Track.objects.get(pk=track.pk)
        self.assertEqual(track.mpd_id, MockMpdClient.PLAYLIST[0]['id'])
