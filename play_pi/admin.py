from django.contrib import admin
from models import *


@admin.register(Artist, Album, Track, Playlist, PlaylistConnection)
class defaultAdmin(admin.ModelAdmin):
    pass