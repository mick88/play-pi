# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def import_credentials(apps, schema_editor):
    from django.conf import settings
    if all([settings.GPLAY_USER, settings.GPLAY_PASS, settings.DEVICE_ID]):
        GoogleCredentials = apps.get_model('play_pi', 'GoogleCredentials')
        Site = apps.get_model('sites', 'Site')
        credentials = GoogleCredentials.objects.create(
            username=settings.GPLAY_USER,
            password=settings.GPLAY_PASS,
            device_id=settings.DEVICE_ID,
        )
        credentials.sites.add(Site.objects.get_current())


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('play_pi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enable', models.BooleanField(default=True)),
                ('username', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=70)),
                ('device_id', models.CharField(max_length=16)),
                ('sites', models.ManyToManyField(related_name='google_credentials', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Google Play Music Credentials',
                'verbose_name_plural': 'Google Play Music Credentials',
            },
        ),
        migrations.RunPython(import_credentials),
    ]
