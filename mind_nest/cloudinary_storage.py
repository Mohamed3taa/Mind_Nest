"""
Custom Cloudinary storage backend for Django.
Uses cloudinary library directly instead of django-cloudinary-storage
which has compatibility issues with Django 5.x.
"""
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.conf import settings
import os


class CloudinaryMediaStorage(Storage):
    """
    Custom storage that uploads media files to Cloudinary.
    """

    def __init__(self):
        config = getattr(settings, 'CLOUDINARY_STORAGE', {})
        cloudinary.config(
            cloud_name = config.get('CLOUD_NAME'),
            api_key    = config.get('API_KEY'),
            api_secret = config.get('API_SECRET'),
        )

    def _open(self, name, mode='rb'):
        raise NotImplementedError("Cannot open files from Cloudinary storage")

    def _save(self, name, content):
        # Remove extension — Cloudinary adds it automatically
        public_id = os.path.splitext(name)[0]
        result = cloudinary.uploader.upload(
            content,
            public_id = public_id,
            overwrite = True,
            resource_type = 'auto',
        )
        # Return the path that will be stored in the DB
        return result['public_id'] + '.' + result['format']

    def url(self, name):
        if not name:
            return ''
        # If already a full URL, return as-is
        if name.startswith('http'):
            return name
        # Build Cloudinary URL
        public_id = os.path.splitext(name)[0]
        ext = os.path.splitext(name)[1]
        return cloudinary.CloudinaryImage(public_id).build_url(
            secure=True
        ) + ext if ext else cloudinary.CloudinaryImage(public_id).build_url(secure=True)

    def exists(self, name):
        return False  # Always allow overwrite

    def delete(self, name):
        public_id = os.path.splitext(name)[0]
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass
