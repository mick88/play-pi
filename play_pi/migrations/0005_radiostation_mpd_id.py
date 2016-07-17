# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play_pi', '0004_auto_20160717_0713'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiostation',
            name='mpd_id',
            field=models.IntegerField(default=0),
        ),
    ]
