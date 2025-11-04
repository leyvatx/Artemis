"""
Django test settings for Artemis API
"""

from .base import *

# Use PostgreSQL for tests (same as production)
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

# Disable password hashers for speed in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations during testing
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Settings for faster tests
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Test-specific settings
SIMPLE_JWT['ALGORITHM'] = 'HS256'

# Disable CORS checks during testing
CORS_ALLOWED_ORIGINS = ['http://localhost', 'http://127.0.0.1']
