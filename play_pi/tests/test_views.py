from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse


class ViewTest(TestCase):
    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Now playing')
