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
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }

# Static files — WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media — Cloudinary for production (persists across deploys)
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')
if CLOUDINARY_URL:
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        cloudinary.config(cloudinary_url=CLOUDINARY_URL)
        INSTALLED_APPS = (
            [app for app in INSTALLED_APPS if app != 'django.contrib.staticfiles']
            + ['cloudinary_storage', 'django.contrib.staticfiles', 'cloudinary']
        )
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        MEDIA_URL = 'https://res.cloudinary.com/' + cloudinary.config().cloud_name + '/'
    except Exception:
        MEDIA_URL  = '/media/'
        MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Security
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# Email — Resend via django-anymail
INSTALLED_APPS += ['anymail']
EMAIL_BACKEND   = 'anymail.backends.resend.EmailBackend'
ANYMAIL         = {'RESEND_API_KEY': os.environ.get('RESEND_API_KEY', '')}
DEFAULT_FROM_EMAIL = 'Mind Nest <onboarding@resend.dev>'
