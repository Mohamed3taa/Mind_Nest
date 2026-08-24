"""
Production settings for Mind Nest — Railway deployment.
"""

from .settings import *
import os
import dj_database_url

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
ALLOWED_HOSTS = ['*']

# Database — Railway provides DATABASE_URL automatically
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    raise Exception("DATABASE_URL environment variable is not set!")

# Static files — WhiteNoise serves from staticfiles/
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media — Cloudinary for persistent file storage
_cloudinary_url = os.environ.get('CLOUDINARY_URL', '')
if _cloudinary_url:
    # Parse cloudinary://key:secret@cloud_name
    import re
    match = re.match(r'cloudinary://(\w+):(\S+)@(\S+)', _cloudinary_url)
    if match:
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': match.group(3),
            'API_KEY':    match.group(1),
            'API_SECRET': match.group(2),
        }
    INSTALLED_APPS = ['cloudinary_storage'] + list(INSTALLED_APPS) + ['cloudinary']
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Security
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# Email — Resend via django-anymail
INSTALLED_APPS = list(INSTALLED_APPS) + ['anymail']
EMAIL_BACKEND      = 'anymail.backends.resend.EmailBackend'
ANYMAIL            = {'RESEND_API_KEY': os.environ.get('RESEND_API_KEY', '')}
DEFAULT_FROM_EMAIL = 'Mind Nest <onboarding@resend.dev>'
