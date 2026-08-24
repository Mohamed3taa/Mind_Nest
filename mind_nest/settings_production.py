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
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media — Cloudinary
# Loaded ONLY at runtime (not during collectstatic build step)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'bqgsojjc',
    'API_KEY':    '936884367462252',
    'API_SECRET': 'H9ctaiwFaP0Pm4IBRBL20zAbbbk',
}
INSTALLED_APPS = list(INSTALLED_APPS) + ['cloudinary_storage', 'cloudinary']
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

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
