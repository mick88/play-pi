from django.contrib.sites.models import Site
from django.db import models


class GoogleCredentials(models.Model):
	enable = models.BooleanField(blank=True)
	username = models.EmailField()
	password = models.CharField(max_length=70)
	device_id = models.CharField(max_length=16)
	sites = models.ManyToManyField(Site, related_name='google_credentials')

	def __unicode__(self):
		return self.username

	class Meta:
		verbose_name = 'Google Play Music Credentials'
		verbose_name_plural = 'Google Play Music Credentials'

class Artist(models.Model):
	name = models.CharField(max_length=200, unique=True)
	art_url = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name


class Album(models.Model):
	name = models.CharField(max_length=200)
	artist = models.ForeignKey(Artist)
	year = models.IntegerField(default=0)
	art_url = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name
	
	class Meta:
		unique_together = ("name", "artist")
	

class Track(models.Model):
	name = models.CharField(max_length=200)
	artist = models.ForeignKey(Artist)
	album = models.ForeignKey(Album)
	stream_id = models.CharField(max_length=100)
	track_no = models.IntegerField(default=0)
	mpd_id = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name


class Playlist(models.Model):
	name = models.CharField(max_length=200)
	pid = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

	def get_art(self):
		pc = PlaylistConnection.objects.filter(playlist=self)[0]
		track = pc.track
		artist = track.artist
		return artist.art_url

	art_url = property(get_art)


class PlaylistConnection(models.Model):
	track = models.ForeignKey(Track)
	playlist = models.ForeignKey(Playlist)

	def __unicode__(self):
		return u'{playlist} / {track}'.format(
			track=self.track,
			playlist=self.playlist,
		)