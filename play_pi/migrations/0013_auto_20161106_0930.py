# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-06 15:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play_pi', '0012_track_last_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='radiostation',
            name='mpd_id',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='track',
            name='mpd_id',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]