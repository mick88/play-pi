from settings import *

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'radio-pi',
        'TIMEOUT': DEFAULT_CACHE_TIME,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}