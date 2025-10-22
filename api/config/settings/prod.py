from .base import *
import os

# Ensure production mode
DEBUG = False

# Hosts allowed to serve the application. Prefer configuring via env var
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'yourdomain.com').split(',')

# Production secret key - MUST be provided via environment in real deployments
SECRET_KEY = os.getenv('SECRET_KEY', 'your-production-secret-key')

# Database for production (example MySQL settings). Replace via env in real deploys.
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME', 'artemis'),
        'USER': os.getenv('DB_USER', 'your_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# Security settings recommended for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True