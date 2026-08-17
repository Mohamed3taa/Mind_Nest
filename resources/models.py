from django.db import models
from django.contrib.auth.models import User


class ResourceType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, default='bi-link-45deg')

    def __str__(self):
        return self.name


class Resource(models.Model):
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resources')
    resource_type = models.ForeignKey(ResourceType, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='resources')
    title         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    link          = models.URLField(max_length=500)
    is_favorite   = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
