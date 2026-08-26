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

# Database
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    raise Exception("DATABASE_URL is not set!")

# Static files — WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media — Cloudinary
# DISABLE_CLOUDINARY=1 during collectstatic build to avoid 0 files issue
if not os.environ.get('DISABLE_CLOUDINARY'):
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': 'bqgsojjc',
        'API_KEY':    '936884367462252',
        'API_SECRET': 'H9ctaiwFaP0Pm4IBRBL20zAbbbk',
    }
    INSTALLED_APPS = list(INSTALLED_APPS) + ['cloudinary']
    STORAGES = {
        'default': {
            'BACKEND': 'mind_nest.cloudinary_storage.CloudinaryMediaStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    MEDIA_URL = 'https://res.cloudinary.com/bqgsojjc/'
else:
    # Build time — use local storage + whitenoise for static
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Security
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# Email — Resend
INSTALLED_APPS = list(INSTALLED_APPS) + ['anymail']
EMAIL_BACKEND      = 'anymail.backends.resend.EmailBackend'
ANYMAIL            = {'RESEND_API_KEY': os.environ.get('RESEND_API_KEY', '')}
DEFAULT_FROM_EMAIL = 'Mind Nest <onboarding@resend.dev>'
