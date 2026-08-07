from django.contrib import admin
from .models import AIConversation, AIMessage

class AIMessageInline(admin.TabularInline):
    model  = AIMessage
    extra  = 0
    fields = ('role', 'content', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    inlines      = [AIMessageInline]

@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display  = ('conversation', 'role', 'created_at')
    list_filter   = ('role',)
