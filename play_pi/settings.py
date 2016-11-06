import os
from gmusicapi import Webclient

# Django settings for play_pi project.

DEBUG = True

GPLAY_USER = "" # Define these in local_settings.py, not here
GPLAY_PASS = "" # Define these in local_settings.py, not here
DEVICE_ID = "" # Define these in local_settings.py, not here

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__)) + '/..'
APACHE_ROOT = os.path.join(PROJECT_PATH, 'apache2')
STATIC_ROOT = os.path.join(APACHE_ROOT, 'static')
MEDIA_ROOT = os.path.join(APACHE_ROOT, 'media')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_PATH, 'play-pi.db'),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DEFAULT_CACHE_TIME = 300

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4f)-90h^38b8xr3wsa6fo_8-ot!e1xo__*6pz3g7k(9zqj)s-l'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'play_pi.context_processors.mpd_status',
                'dealer.contrib.django.context_processor',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
        },
    }
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'play_pi.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'play_pi.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'bootstrap3',
    'debug_toolbar',
    'rest_framework',
    'play_pi',
    'api',
    'hardware',
)

try:
    # Optional: Include django extensions if installed
    # pip install django-extensions
    import django_extensions
    INSTALLED_APPS += 'django_extensions',
except ImportError:
    pass

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'play_pi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate':True,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'api.auth.SessionAuthenticationNoCsrf',
    ),
    'PAGE_SIZE': 50,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# MPD deamon settings
MPD_ADDRESS = 'localhost'
MPD_PORT = 6600

# Defines whether login is required to view data
LOGIN_REQUIRED = False
# Defines whether login is required to control playback, queue etc
PLAYBACK_CONTROL_LOGIN_REQUIRED = False


def should_show_debug_toolbar(request):
    """
    Custom logic to showing debug toolbar
    Enables toolbar when developing using vagrant (client ip is not localhost)
    Original: debug_toolbar.middleware.show_toolbar
    """
    from django.conf import settings
    return bool(settings.DEBUG) and not request.is_ajax()

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': should_show_debug_toolbar,
}

DEALER_TYPE = 'git'
DEALER_PATH = PROJECT_PATH

try:
    from local_settings import *
except ImportError:
    pass
