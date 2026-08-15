"""
Production settings for Mind Nest.
Used when deploying to Railway / Render.
"""

from .settings import *
import os
import dj_database_url

# Security
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = ['*']  # Railway sets the host automatically

# Database — use DATABASE_URL from Railway
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }

# Static files — WhiteNoise serves static files in production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT  = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
