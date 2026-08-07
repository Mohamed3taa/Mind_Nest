from django.contrib import admin
from .models import ResourceType, Resource

@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'resource_type', 'is_favorite', 'created_at')
    search_fields = ('title', 'description')
    list_filter   = ('resource_type', 'is_favorite')
