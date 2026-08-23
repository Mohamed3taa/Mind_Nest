from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from planner.models import Task
from notes.models import Note
from resources.models import Resource
from ai_assistant.models import AIConversation
from quizzes.models import Quiz, QuizAttempt
import json


@login_required
def index(request):
    user = request.user

    total_tasks     = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, is_completed=True).count()
    pending_tasks   = total_tasks - completed_tasks
    total_notes     = Note.objects.filter(user=user).count()
    total_resources = Resource.objects.filter(user=user).count()
    total_ai_chats  = AIConversation.objects.filter(user=user).count()

    # Quiz stats
    total_quizzes   = Quiz.objects.filter(user=user, is_active=True).count()
    total_attempts  = QuizAttempt.objects.filter(user=user).count()
    best_attempt    = QuizAttempt.objects.filter(user=user).order_by('-percentage').first()
    quiz_best_score = round(best_attempt.percentage, 1) if best_attempt else None

    recent_tasks     = Task.objects.filter(user=user).order_by('-created_at')[:5]
    recent_notes     = Note.objects.filter(user=user).order_by('-updated_at')[:5]
    recent_resources = Resource.objects.filter(user=user).order_by('-created_at')[:4]

    today     = timezone.now().date()
    next_week = today + timezone.timedelta(days=7)
    upcoming_tasks = Task.objects.filter(
        user=user,
        is_completed=False,
        due_date__range=[today, next_week]
    ).order_by('due_date')[:5]

    completion_pct = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

    priority_data = {
        'labels': ['High', 'Medium', 'Low'],
        'data': [
            Task.objects.filter(user=user, priority='high').count(),
            Task.objects.filter(user=user, priority='medium').count(),
            Task.objects.filter(user=user, priority='low').count(),
        ],
        'colors': ['#ef4444', '#f59e0b', '#22c55e']
    }

    status_data = {
        'labels': ['To Do', 'In Progress', 'Done'],
        'data': [
            Task.objects.filter(user=user, status='todo').count(),
            Task.objects.filter(user=user, status='in_progress').count(),
            Task.objects.filter(user=user, status='done').count(),
        ],
        'colors': ['#94a3b8', '#f59e0b', '#22c55e']
    }

    overview_data = {
        'labels': ['Tasks', 'Notes', 'Resources', 'AI Chats', 'Quizzes'],
        'data': [total_tasks, total_notes, total_resources, total_ai_chats, total_quizzes],
        'colors': ['#89b4fa', '#cba6f7', '#a6e3a1', '#f9e2af', '#f38ba8']
    }

    context = {
        'total_tasks':      total_tasks,
        'completed_tasks':  completed_tasks,
        'pending_tasks':    pending_tasks,
        'total_notes':      total_notes,
        'total_resources':  total_resources,
        'total_ai_chats':   total_ai_chats,
        'total_quizzes':    total_quizzes,
        'total_attempts':   total_attempts,
        'quiz_best_score':  quiz_best_score,
        'recent_tasks':     recent_tasks,
        'recent_notes':     recent_notes,
        'recent_resources': recent_resources,
        'upcoming_tasks':   upcoming_tasks,
        'completion_pct':   completion_pct,
        'today':            today,
        'priority_data':    json.dumps(priority_data),
        'status_data':      json.dumps(status_data),
        'overview_data':    json.dumps(overview_data),
    }
    return render(request, 'dashboard/index.html', context)
