"""
Django test settings for Artemis API
"""

from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'artemis_test',
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

SIMPLE_JWT['ALGORITHM'] = 'HS256'

CORS_ALLOWED_ORIGINS = ['http://localhost', 'http://127.0.0.1']
