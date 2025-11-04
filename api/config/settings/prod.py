from .base import *
import os
from decouple import config

# Ensure production mode
DEBUG = False

# Hosts allowed to serve the application. Prefer configuring via env var
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='yourdomain.com').split(',')

# Production secret key - MUST be provided via environment in real deployments
SECRET_KEY = config('SECRET_KEY')

# PostgreSQL Database for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': True,
    }
}

# Security settings recommended for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True