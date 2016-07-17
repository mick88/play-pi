# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


RADIO_STATIONS = [
    ("Radio NOVA 100FM", "http://31.14.40.241:9752/;stream/1"),
    ("Nova Classic Rock", "http://31.14.40.241:9760/;stream/1"),
    ("Nova 60s", "http://31.14.40.241:9748/;stream/1"),
    ("Nova 70s", "http://31.14.40.241:9750/;stream/1"),
    ("Nova 80s", "http://31.14.40.241:9758/;stream/1"),
    ("Nova 90s", "http://31.14.40.241:9756/;stream/1"),
    ("Nova 00s", "http://31.14.40.241:9752/;stream/1"),
    ("Nova Chill", "http://31.14.40.241:9762/;stream/1"),
]


def populate_radio_stations(apps, schema_editor):
    RadioStation = apps.get_model('play_pi', 'RadioStation')
    RadioStation.objects.bulk_create([RadioStation(name=name, url=url) for name, url in RADIO_STATIONS])


def delete_radiostations(apps, schema_editor):
    RadioStation = apps.get_model('play_pi', 'RadioStation')
    RadioStation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('play_pi', '0003_radiostation'),
    ]

    operations = [
        migrations.RunPython(populate_radio_stations, delete_radiostations),
    ]
