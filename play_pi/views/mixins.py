# -*- coding: utf-8 -*-
import random

from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.utils.cache import patch_response_headers
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)


class CacheMixin(object):
    cache_timeout = settings.DEFAULT_CACHE_TIME

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class CacheControlMixin(object):
    cache_timeout = settings.DEFAULT_CACHE_TIME

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        response = super(CacheControlMixin, self).dispatch(*args, **kwargs)
        patch_response_headers(response, self.get_cache_timeout())
        return response


class JitterCacheMixin(CacheControlMixin):
    cache_range = [40, 80]

    def get_cache_range(self):
        return self.cache_range

    def get_cache_timeout(self):
        return random.randint(*self.get_cache_range())


class CheckLoginMixin(AccessMixin):
    """
    Checks whether login is required and is so,
    redirects user to login if not authenticated.
    """
    # Tells whether this view controls playback
    playback_control = False

    def is_playback_control(self, request):
        """Tells whether this view controls playback"""
        return self.playback_control

    # noinspection PyUnresolvedReferences
    def dispatch(self, request, *args, **kwargs):
        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            return self.handle_no_permission()
        elif settings.PLAYBACK_CONTROL_LOGIN_REQUIRED and self.is_playback_control(request) and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(CheckLoginMixin, self).dispatch(request, *args, **kwargs)