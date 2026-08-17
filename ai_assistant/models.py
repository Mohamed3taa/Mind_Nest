from django.db import models
from django.contrib.auth.models import User


class AIConversation(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title      = models.CharField(max_length=200, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class AIMessage(models.Model):

    class Role(models.TextChoices):
        USER      = 'user',      'User'
        ASSISTANT = 'assistant', 'Assistant'

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role         = models.CharField(max_length=10, choices=Role.choices)
    content      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"


class UploadedDocument(models.Model):

    class DocType(models.TextChoices):
        PDF  = 'pdf',  'PDF'
        DOCX = 'docx', 'Word Document'
        TXT  = 'txt',  'Text File'

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title          = models.CharField(max_length=200)
    file           = models.FileField(upload_to='ai_documents/')
    doc_type       = models.CharField(max_length=10, choices=DocType.choices)
    extracted_text = models.TextField(blank=True)
    uploaded_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"
