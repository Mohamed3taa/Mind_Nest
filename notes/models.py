from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name       = models.CharField(max_length=100)
    color      = models.CharField(max_length=7, default='#6c757d')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Note(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    category   = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags       = models.ManyToManyField(Tag, blank=True, related_name='notes')
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    is_pinned  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return self.title
