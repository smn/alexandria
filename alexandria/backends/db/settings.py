import os
from os.path import join, abspath, dirname

DEBUG = True

APP_ROOT = abspath(join(dirname(__file__),'..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db/alexandria_dev.db',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'alexandria.backends.db'
)

TEMPLATE_DIRS = (
    join(APP_ROOT, 'db/templates')
)

MEDIA_ROOT = join(APP_ROOT, 'db', 'media')
MEDIA_URL = '/static/'


ROOT_URLCONF = 'alexandria.backends.db.urls'

INSTALLED_APPS = (
    'alexandria.backends.db',
    'django.contrib.admin',
    'django.contrib.contenttypes',
)