from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.apps import apps
from play_pi.models import *


class Command(BaseCommand):
    help = 'Initializes the database with your Google Music library'

    @transaction.atomic()
    def handle(self, *args, **options):
        app = apps.get_app_config('play_pi')
        api = app.get_api()

        self.stdout.write('Connected to Google Music, downloading data...')
        library = api.get_all_songs()
        self.stdout.write('Data downloaded!')
        self.stdout.write('Clearing DB...')
        cursor = connection.cursor()
        # This can take a long time using ORM commands on the Pi, so lets Truncate
        cursor.execute('DELETE FROM ' + Track._meta.db_table)
        cursor.execute('DELETE FROM ' + Album._meta.db_table)
        cursor.execute('DELETE FROM ' + Artist._meta.db_table)
        cursor.execute('DELETE FROM ' + Playlist._meta.db_table)
        cursor.execute('DELETE FROM ' + PlaylistConnection._meta.db_table)
        self.stdout.write('Parsing new data...')

        # Easier to keep track of who we've seen like this...
        artists = set()
        albums = set()
        count = len(library)
        self.stdout.write(str(count) + ' tracks found')
        i = 0
        created_tracks = []
        for song in library:
            i += 1

            artist_name = song['artist'] or song['albumArtist'] or "Unknown Artist"

            if artist_name not in artists:
                try:
                    art_url = song['artistArtRef'][0]['url']
                except:
                    art_url = ''
                    self.stderr.write(u"No artist art found for {}".format(artist_name))
                artist = Artist.objects.create(
                    name=artist_name,
                    art_url=art_url,
                )

                artists.add(artist_name)
                self.stdout.write(u'Added artist: {}'.format(artist))
                self.stdout.write(u'{}/{} tracks completed'.format(i, count))
            else:
                artist = Artist.objects.get(name=artist_name)

            album_name = song['album']
            if (album_name, artist_name) not in albums:
                try:
                    art_url = song['albumArtRef'][0]['url']
                except:
                    art_url = ''
                    self.stderr.write(u"No album art found for {}".format(album_name))
                album = Album(
                    name=album_name,
                    artist = artist,
                    year=song.get('year', 0),
                    art_url=art_url,
                )

                album.save()
                albums.add((album_name, artist_name))
            else:
                album = Album.objects.get(name=album_name, artist=artist)

            track = Track(
                artist=artist,
                album=album,
                name=song['title'],
                stream_id=song['id'],
                track_no=song.get('trackNumber', 0)
            )
            created_tracks.append(track)
        Track.objects.bulk_create(created_tracks)

        self.stdout.write('All tracks saved!')
        self.stdout.write('Getting Playlists...')

        playlists = api.get_all_user_playlist_contents()
        for playlist in playlists:
            p = Playlist.objects.create(
                pid=playlist['id'],
                name = playlist['name'],
            )
            connections = []
            for entry in playlist['tracks']:
                try:
                    track = Track.objects.get(stream_id=entry['trackId'])
                    playlist_connection = PlaylistConnection(
                        playlist=p,
                        track = track,
                    )
                    connections.append(playlist_connection)
                except Exception as e:
                    self.stderr.write(e.message)

            PlaylistConnection.objects.bulk_create(connections)

        self.stdout.write('Library saved!')
