from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import QuerySet


class CredentialsQuerySet(QuerySet):
	def enabled(self):
		site = Site.objects.get_current()
		return site.google_credentials.filter(enable=True)

class GoogleCredentials(models.Model):
	enable = models.BooleanField(blank=True, default=True)
	username = models.EmailField()
	password = models.CharField(max_length=70)
	device_id = models.CharField(max_length=16)
	sites = models.ManyToManyField(Site, related_name='google_credentials')

	objects = CredentialsQuerySet.as_manager()

	def __unicode__(self):
		return self.username

	class Meta:
		verbose_name = 'Google Play Music Credentials'
		verbose_name_plural = 'Google Play Music Credentials'

class Artist(models.Model):
	name = models.CharField(max_length=200, unique=True)
	art_url = models.CharField(max_length=200)

	def get_absolute_url(self):
		return reverse('artist', args=[self.id])

	def __unicode__(self):
		return self.name


class Album(models.Model):
	name = models.CharField(max_length=200)
	artist = models.ForeignKey(Artist)
	year = models.IntegerField(default=0)
	art_url = models.CharField(max_length=200)

	def get_absolute_url(self):
		return reverse('album', args=[self.id])

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

	def get_absolute_url(self):
		return reverse('playlist', args=[self.id])

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


class RadioStation(models.Model):
	name = models.CharField(max_length=70)
	url = models.URLField()
	mpd_id = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name
