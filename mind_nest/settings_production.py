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

# Media
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# Email — SMTP via Gmail (port 465/SSL for Railway compatibility)
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 465
EMAIL_USE_SSL       = True
EMAIL_USE_TLS       = False
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('EMAIL_HOST_USER', '')

# Fall back to console if credentials missing
if not EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
