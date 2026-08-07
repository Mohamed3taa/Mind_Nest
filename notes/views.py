from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Note, Category, Tag
from .forms import NoteForm, CategoryForm


def save_tags(note, tags_input, user):
    """Helper — parse comma-separated tags and attach to note"""
    note.tags.clear()
    if tags_input:
        for name in tags_input.split(','):
            name = name.strip().lower()
            if name:
                tag, _ = Tag.objects.get_or_create(user=user, name=name)
                note.tags.add(tag)


@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user)

    # Filtering
    category_id = request.GET.get('category', '')
    search      = request.GET.get('search', '')
    tag_name    = request.GET.get('tag', '')

    if category_id:
        notes = notes.filter(category_id=category_id)
    if search:
        notes = notes.filter(title__icontains=search) | notes.filter(content__icontains=search)
        notes = notes.distinct()
    if tag_name:
        notes = notes.filter(tags__name=tag_name)

    categories = Category.objects.filter(user=request.user)
    tags       = Tag.objects.filter(user=request.user)
    form       = NoteForm(user=request.user)
    cat_form   = CategoryForm()

    context = {
        'notes':       notes,
        'categories':  categories,
        'tags':        tags,
        'form':        form,
        'cat_form':    cat_form,
        'current_cat': category_id,
        'current_search': search,
        'current_tag': tag_name,
    }
    return render(request, 'notes/note_list.html', context)


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            save_tags(note, form.cleaned_data.get('tags_input', ''), request.user)
            messages.success(request, 'Note created successfully!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('notes:note_list')


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST, instance=note)
        if form.is_valid():
            form.save()
            save_tags(note, form.cleaned_data.get('tags_input', ''), request.user)
            messages.success(request, 'Note updated successfully!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('notes:note_list')


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
    return redirect('notes:note_list')


@login_required
def note_toggle_pin(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.is_pinned = not note.is_pinned
        note.save()
        messages.success(request, 'Note pinned!' if note.is_pinned else 'Note unpinned.')
    return redirect('notes:note_list')


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, f'Category "{cat.name}" created!')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('notes:note_list')


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
    return redirect('notes:note_list')
