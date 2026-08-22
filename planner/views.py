from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):
    tasks    = Task.objects.filter(user=request.user)
    priority = request.GET.get('priority', '')
    status   = request.GET.get('status', '')
    search   = request.GET.get('search', '')

    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    if search:
        tasks = tasks.filter(title__icontains=search)

    paginator = Paginator(tasks, 8)
    page      = request.GET.get('page', 1)
    tasks     = paginator.get_page(page)

    all_count      = Task.objects.filter(user=request.user).count()
    todo_count     = Task.objects.filter(user=request.user, status='todo').count()
    progress_count = Task.objects.filter(user=request.user, status='in_progress').count()
    done_count     = Task.objects.filter(user=request.user, status='done').count()

    context = {
        'tasks':            tasks,
        'form':             TaskForm(),
        'all_count':        all_count,
        'todo_count':       todo_count,
        'progress_count':   progress_count,
        'done_count':       done_count,
        'current_priority': priority,
        'current_status':   status,
        'current_search':   search,
        'today':            timezone.now().date(),
    }
    return render(request, 'planner/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task      = form.save(commit=False)
            task.user = request.user
            # sync is_completed with status
            task.is_completed = (task.status == 'done')
            task.save()
            messages.success(request, 'Task created successfully!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('planner:task_list')


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save(commit=False)
            # keep is_completed in sync with status
            updated_task.is_completed = (updated_task.status == 'done')
            updated_task.save()
            messages.success(request, 'Task updated successfully!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('planner:task_list')


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
    return redirect('planner:task_list')


@login_required
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.is_completed = not task.is_completed
        task.status       = 'done' if task.is_completed else 'todo'
        task.save()
        return JsonResponse({'is_completed': task.is_completed, 'status': task.status})
    return JsonResponse({'error': 'Invalid request'}, status=400)
