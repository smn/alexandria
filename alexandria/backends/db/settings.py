DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'alexandria_dev',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'alexandria.backends.db'
)
