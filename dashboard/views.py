from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from planner.models import Task
from notes.models import Note
from resources.models import Resource
from ai_assistant.models import AIConversation


@login_required
def index(request):
    user = request.user

    # --- Stats ---
    total_tasks     = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, is_completed=True).count()
    pending_tasks   = total_tasks - completed_tasks
    total_notes     = Note.objects.filter(user=user).count()
    total_resources = Resource.objects.filter(user=user).count()
    total_ai_chats  = AIConversation.objects.filter(user=user).count()

    # --- Recent items ---
    recent_tasks     = Task.objects.filter(user=user).order_by('-created_at')[:5]
    recent_notes     = Note.objects.filter(user=user).order_by('-updated_at')[:5]
    recent_resources = Resource.objects.filter(user=user).order_by('-created_at')[:4]

    # --- Upcoming tasks (due in next 7 days, not completed) ---
    today     = timezone.now().date()
    next_week = today + timezone.timedelta(days=7)
    upcoming_tasks = Task.objects.filter(
        user=user,
        is_completed=False,
        due_date__range=[today, next_week]
    ).order_by('due_date')[:5]

    # --- Task completion percentage ---
    completion_pct = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

    context = {
        'total_tasks':     total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks':   pending_tasks,
        'total_notes':     total_notes,
        'total_resources': total_resources,
        'total_ai_chats':  total_ai_chats,
        'recent_tasks':    recent_tasks,
        'recent_notes':    recent_notes,
        'recent_resources': recent_resources,
        'upcoming_tasks':  upcoming_tasks,
        'completion_pct':  completion_pct,
        'today':           today,
    }
    return render(request, 'dashboard/index.html', context)
