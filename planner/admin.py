from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'priority', 'status', 'due_date', 'is_completed')
    search_fields = ('title',)
    list_filter   = ('priority', 'status', 'is_completed')
