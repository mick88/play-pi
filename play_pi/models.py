from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from sortedm2m.fields import SortedManyToManyField


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
    art_url = models.CharField(max_length=200, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('artist', args=[self.id])

    def __unicode__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, null=True, blank=True)
    year = models.IntegerField(default=0)
    art_url = models.CharField(max_length=200, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('album', args=[self.id])

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ("name", "artist")


class BaseMpdTrack(models.Model):
    """
    Base class for items playable with MPD
    contains essentials such as mpd id
    """
    mpd_id = models.IntegerField(default=0)

    class Meta:
        abstract = True

    @classmethod
    def type_name(cls):
        """ Should return either "track" or "radio" string """
        raise NotImplementedError


class Track(BaseMpdTrack):
    RATING_NONE = 0
    RATING_THUMBS_DOWN = 1
    RATING_THUMBS_UP = 5
    RATING_CHOICES = (
        (RATING_NONE, u'No rating'),
        (RATING_THUMBS_DOWN, u'Thumbs down'),
        (RATING_THUMBS_UP, u'Thumbs up'),
    )

    name = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist)
    album = models.ForeignKey(Album, null=True, blank=True)
    stream_id = models.CharField(max_length=100)
    track_no = models.IntegerField(default=0)
    rating = models.SmallIntegerField(default=0, choices=RATING_CHOICES)

    @classmethod
    def type_name(cls):
        return 'track'

    @property
    def art_url(self):
        return self.artist.art_url

    def __unicode__(self):
        return self.name


class Playlist(models.Model):
    name = models.CharField(max_length=200)
    pid = models.CharField(max_length=200)
    tracks = SortedManyToManyField(Track, through='PlaylistConnection', related_name='playlists')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('playlist', args=[self.id])

    def get_art(self):
        artist = Artist.objects.filter(track__playlists=self).first()
        return artist.art_url

    art_url = property(get_art)


class PlaylistConnection(models.Model):
    track = models.ForeignKey(Track)
    playlist = models.ForeignKey(Playlist)
    sort_value = models.IntegerField(default=0)

    _sort_field_name = 'sort_value'

    def __unicode__(self):
        return u'{playlist} / {track}'.format(
            track=self.track,
            playlist=self.playlist,
        )


class RadioStation(BaseMpdTrack):
    name = models.CharField(max_length=70)
    url = models.URLField()
    order = models.IntegerField(default=0)

    @classmethod
    def type_name(cls):
        return 'radio'

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = 'order',


@receiver(post_save, sender=RadioStation, dispatch_uid='on_model_update_invalidate_cache')
@receiver(post_delete, sender=RadioStation, dispatch_uid='on_model_update_invalidate_cache')
def on_model_update(sender, instance, **kwargs):
    from play_pi.utils import invalidate_cache
    invalidate_cache()
