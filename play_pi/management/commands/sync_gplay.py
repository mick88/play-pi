import datetime

import pytz
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.models.query_utils import Q

from play_pi.models import *


class Command(BaseCommand):
    help = 'Synchronizes local database with Google Play Music'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--create-thumbsup', action='store_true', dest='create_thumbsup', default=False, help='Create playlist with thumbs-up songs')

    def delete_entries(self):
        self.stdout.write('Clearing DB... ', ending='')
        cursor = connection.cursor()
        # This can take a long time using ORM commands on the Pi, so lets Truncate
        cursor.execute('DELETE FROM ' + Track._meta.db_table)
        cursor.execute('DELETE FROM ' + Album._meta.db_table)
        cursor.execute('DELETE FROM ' + Artist._meta.db_table)
        cursor.execute('DELETE FROM ' + Playlist._meta.db_table)
        cursor.execute('DELETE FROM ' + PlaylistConnection._meta.db_table)
        self.stdout.write('done')

    def import_tracks(self, library):
        # Easier to keep track of who we've seen like this...
        artists = set()
        albums = set()
        count = len(library)
        self.stdout.write('Downloading {} tracks...'.format(count))
        i = 0
        created_tracks = []

        def get_artist(name, art_url):
            if name not in artists:
                artist = Artist.objects.create(
                    name=name,
                    art_url=art_url,
                )

                artists.add(name)
                return artist
            else:
                artist = Artist.objects.get(name=name)
                return artist

        for song in library:
            i += 1

            artist_name = song['artist'] or song['albumArtist'] or "Unknown Artist"

            try:
                art_url = song['artistArtRef'][0]['url']
            except:
                art_url = ''

            artist = get_artist(artist_name, art_url)
            album_name = song['album']

            if album_name:
                album_artist_name = song['albumArtist']
                album_artist = get_artist(album_artist_name, '') if album_artist_name else None
                album_key = (album_name, album_artist_name)
                if album_key not in albums:
                    try:
                        art_url = song['albumArtRef'][0]['url']
                    except:
                        art_url = ''
                    album = Album(
                        name=album_name,
                        artist=album_artist,
                        year=song.get('year', 0),
                        art_url=art_url,
                    )

                    album.save()
                    albums.add(album_key)
                else:
                    album = Album.objects.get(name=album_name, artist=album_artist)
            else:
                album = None

            last_modified_timestamp = song.get('lastModifiedTimestamp', None)
            if last_modified_timestamp:
                unix_timestamp = float(last_modified_timestamp) / 1000000
                last_modified = datetime.datetime.fromtimestamp(unix_timestamp, tz=pytz.timezone(settings.TIME_ZONE))
            else:
                last_modified = None
            track = Track(
                artist=artist,
                album=album,
                name=song['title'],
                rating=song.get('rating', Track.RATING_NONE),
                stream_id=song['id'],
                track_no=song.get('trackNumber', 0),
                last_modified=last_modified,
            )
            created_tracks.append(track)
            self.stdout.write(u'{}/{} tracks saved'.format(i, count), ending='\r')
        self.stdout.write('')
        Track.objects.bulk_create(created_tracks)
        return created_tracks

    def import_playlists(self, playlists):
        self.stdout.write('Importing Playlists...', ending='')
        for playlist in playlists:
            p = Playlist.objects.create(
                pid=playlist['id'],
                name=playlist['name'],
            )
            connections = []
            for entry in playlist['tracks']:
                try:
                    track = Track.objects.get(stream_id=entry['trackId'])
                    playlist_connection = PlaylistConnection(
                        playlist=p,
                        track=track,
                    )
                    connections.append(playlist_connection)
                except Exception as e:
                    self.stderr.write(e.message)

            PlaylistConnection.objects.bulk_create(connections)
        self.stdout.write('done')

    def create_thumbs_up_playlist(self):
        thumbs_up_name = u'Thumbs up'
        self.stdout.write(u'Creating "Thumbs up" playlist...', ending=' ')
        if Playlist.objects.filter(name=thumbs_up_name).exists():
            self.stdout.write(u'Playlist {} already exists'.format(thumbs_up_name))
            return
        tracks = Track.objects.filter(rating=Track.RATING_THUMBS_UP).order_by('-last_modified')
        if tracks.exists():
            playlist = Playlist.objects.create(
                name=thumbs_up_name,
            )
            PlaylistConnection.objects.bulk_create(
                [PlaylistConnection(track=track, playlist=playlist) for track in tracks]
            )
            self.stdout.write(u'created with {} tracks'.format(tracks.count()))
        else:
            self.stdout.write(u'no liked songs found in the library.')

    def backup_mpd_ids(self):
        """
        Backs-up mpd ids into a tuple values (mpd_id, stream_id)
        """
        return tuple(Track.objects.filter(~Q(mpd_id=0)).values_list('mpd_id', 'stream_id'))

    def restore_mpd_ids(self, mpd_ids):
        """
        Restores mpd ids into Track objects.
        Looks up Tracks by stream_id
        """
        for mpd_id, stream_id in mpd_ids:
            Track.objects.filter(stream_id=stream_id).update(
                mpd_id=mpd_id,
            )

    @transaction.atomic()
    def handle(self, *args, **options):
        app = apps.get_app_config('play_pi')
        api = app.get_api()

        # Fetching data from Play Music
        self.stdout.write('Connected to Google Music, downloading data...', ending='')
        songs = api.get_all_songs()
        playlists = api.get_all_user_playlist_contents()
        self.stdout.write('done')

        mpd_ids = self.backup_mpd_ids()

        # Writing data to database
        self.delete_entries()
        self.import_tracks(songs)
        # Restore mpd ids so that playback queue is not reset by sync
        self.restore_mpd_ids(mpd_ids)
        self.import_playlists(playlists)
        if options['create_thumbsup']:
            self.create_thumbs_up_playlist()



