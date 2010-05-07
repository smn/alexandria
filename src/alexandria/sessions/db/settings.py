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
    }
}

# For some reason nosedjango breaks over transaction management with sqlite3
# in this project. This avoids the problem by disabling transaction management
# completely. For now this is alright since we need to find a better way
# of testing stuff without a db or a django backend anyway.
if DATABASES['default']['ENGINE'].endswith('sqlite3'):
    DISABLE_TRANSACTION_MANAGEMENT = True

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