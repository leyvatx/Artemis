from .base import *from .base import *



DEBUG = FalseDEBUG = False



ALLOWED_HOSTS = ['yourdomain.com']ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')



# Production settingsSECRET_KEY = os.getenv('SECRET_KEY')

SECRET_KEY = 'your-production-secret-key'

# Add production-specific settings

# Database for productionSECURE_SSL_REDIRECT = True

DATABASES = {SESSION_COOKIE_SECURE = True

    'default': {CSRF_COOKIE_SECURE = True
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'artemis',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True