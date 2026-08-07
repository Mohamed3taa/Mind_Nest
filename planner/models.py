from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):

    class Priority(models.TextChoices):
        LOW    = 'low',    'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH   = 'high',   'High'

    class Status(models.TextChoices):
        TODO       = 'todo',        'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE       = 'done',        'Done'

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority    = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.TODO)
    due_date    = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_completed', 'due_date', '-priority']

    def __str__(self):
        return self.title
