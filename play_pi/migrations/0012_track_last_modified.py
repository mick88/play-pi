# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-06 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('play_pi', '0011_auto_20161031_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='last_modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
