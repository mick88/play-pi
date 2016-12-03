from django.contrib import admin

from models import *
from play_pi.forms import GoogleCredentialsForm


@admin.register(Artist, Album, Playlist, PlaylistConnection)
class DefaultAdmin(admin.ModelAdmin):
    pass


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'rating', 'stream_url']
    search_fields = ['name', 'artist__name', 'album__name']
    list_filter = ['rating']


@admin.register(RadioStation)
class RadioStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order']
    list_editable = ['order']


@admin.register(GoogleCredentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ['username', 'enable']
    form = GoogleCredentialsForm
