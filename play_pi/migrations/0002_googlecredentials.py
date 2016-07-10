# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


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
                ('enable', models.BooleanField()),
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
    ]
