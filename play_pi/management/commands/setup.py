from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction

from play_pi.models import GoogleCredentials


class Command(BaseCommand):
    help = 'Configure Play Pi for access to Google Play Music'

    @transaction.atomic
    def create_google_credentials(self, sites):
        email = raw_input('Google e-mail address:')
        password = raw_input('Google password:')
        self.stdout.write('Now please enter your android device id (IMEI)')
        device_id = raw_input('Device ID:')
        credentials = GoogleCredentials.objects.create(
            username=email,
            password=password,
            device_id=device_id,
        )
        credentials.sites.add(*sites)

    def handle(self, *args, **options):
        self.stdout.write('Setting up Play Pi')
        if GoogleCredentials.objects.filter(enable=True).exists():
            self.stdout.write('Google Credentials already configured and enabled')
        else:
            sites = Site.objects.all()
            self.create_google_credentials(sites)
