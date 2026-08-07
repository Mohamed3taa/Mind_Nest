from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Resource, ResourceType
from .forms import ResourceForm


@login_required
def resource_list(request):
    resources = Resource.objects.filter(user=request.user)

    # Filtering
    type_id     = request.GET.get('type', '')
    search      = request.GET.get('search', '')
    favorite    = request.GET.get('favorite', '')

    if type_id:
        resources = resources.filter(resource_type_id=type_id)
    if search:
        resources = resources.filter(title__icontains=search) | \
                    resources.filter(description__icontains=search)
        resources = resources.distinct()
    if favorite:
        resources = resources.filter(is_favorite=True)

    # Pagination
    paginator = Paginator(resources, 9)
    page      = request.GET.get('page', 1)
    resources = paginator.get_page(page)

    resource_types = ResourceType.objects.all()
    form           = ResourceForm()

    context = {
        'resources':      resources,
        'resource_types': resource_types,
        'form':           form,
        'current_type':   type_id,
        'current_search': search,
        'current_fav':    favorite,
        'total':          Resource.objects.filter(user=request.user).count(),
        'fav_count':      Resource.objects.filter(user=request.user, is_favorite=True).count(),
    }
    return render(request, 'resources/resource_list.html', context)


@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.save()
            messages.success(request, 'Resource added successfully!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('resources:resource_list')


@login_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('resources:resource_list')


@login_required
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted.')
    return redirect('resources:resource_list')


@login_required
def resource_toggle_favorite(request, pk):
    resource = get_object_or_404(Resource, pk=pk, user=request.user)
    if request.method == 'POST':
        resource.is_favorite = not resource.is_favorite
        resource.save()
        return JsonResponse({'is_favorite': resource.is_favorite})
    return JsonResponse({'error': 'Invalid'}, status=400)
