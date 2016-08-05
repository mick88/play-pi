from django.contrib import admin
from models import *
from play_pi.forms import GoogleCredentialsForm


@admin.register(Artist, Album, Track, Playlist, PlaylistConnection)
class DefaultAdmin(admin.ModelAdmin):
    pass


@admin.register(RadioStation)
class RadioStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']


@admin.register(GoogleCredentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ['username', 'enable']
    form = GoogleCredentialsForm
