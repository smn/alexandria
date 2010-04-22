import os
from os.path import join, abspath, dirname

DEBUG = True

APP_ROOT = abspath(join(dirname(__file__),'..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(APP_ROOT,'db','sqlite3','alexandria_dev.db'),
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
        'SUPPORTS_TRANSACTIONS': False,
    }
}

INSTALLED_APPS = (
    'alexandria.sessions.db'
)

TEMPLATE_DIRS = (
    join(APP_ROOT, 'db/templates')
)

MEDIA_ROOT = join(APP_ROOT, 'db', 'media')
MEDIA_URL = '/static/'


ROOT_URLCONF = 'alexandria.sessions.db.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'alexandria.sessions.db',
)

TEST_RUNNER = 'django_nose.run_tests'