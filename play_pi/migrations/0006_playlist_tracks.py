# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play_pi', '0005_radiostation_mpd_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='tracks',
            field=models.ManyToManyField(related_name='playlists', through='play_pi.PlaylistConnection', to='play_pi.Track'),
        ),
    ]
