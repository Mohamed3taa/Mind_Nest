from django.contrib import admin
from .models import Category, Tag, Note

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'user', 'color', 'created_at')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ('name', 'user')
    search_fields = ('name',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'category', 'is_pinned', 'created_at')
    search_fields = ('title', 'content')
    list_filter   = ('category', 'is_pinned')
    filter_horizontal = ('tags',)
