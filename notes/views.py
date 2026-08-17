from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from .models import Note, Category, Tag
from .forms import NoteForm, CategoryForm


def save_tags(note, tags_input, user):
    note.tags.clear()
    if tags_input:
        for name in tags_input.split(','):
            name = name.strip().lower()
            if name:
                tag, _ = Tag.objects.get_or_create(user=user, name=name)
                note.tags.add(tag)


@login_required
def note_list(request):
    notes       = Note.objects.filter(user=request.user)
    category_id = request.GET.get('category', '')
    search      = request.GET.get('search', '')
    tag_name    = request.GET.get('tag', '')

    if category_id:
        notes = notes.filter(category_id=category_id)
    if search:
        notes = (notes.filter(title__icontains=search) |
                 notes.filter(content__icontains=search)).distinct()
    if tag_name:
        notes = notes.filter(tags__name=tag_name)

    paginator = Paginator(notes, 9)
    notes     = paginator.get_page(request.GET.get('page', 1))

    context = {
        'notes':          notes,
        'categories':     Category.objects.filter(user=request.user),
        'tags':           Tag.objects.filter(user=request.user),
        'form':           NoteForm(user=request.user),
        'cat_form':       CategoryForm(),
        'current_cat':    category_id,
        'current_search': search,
        'current_tag':    tag_name,
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
            note      = form.save(commit=False)
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
            cat      = form.save(commit=False)
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


@login_required
def export_note_pdf(request, pk):
    note   = get_object_or_404(Note, pk=pk, user=request.user)
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style  = ParagraphStyle('Title',  parent=styles['Title'],
                                  fontSize=22, textColor=colors.HexColor('#1e1e2e'), spaceAfter=8)
    meta_style   = ParagraphStyle('Meta',   parent=styles['Normal'],
                                  fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=4)
    body_style   = ParagraphStyle('Body',   parent=styles['Normal'],
                                  fontSize=11, leading=18, spaceAfter=6)
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                  fontSize=8, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)

    elements = []
    elements.append(Paragraph(note.title, title_style))

    meta = (f"Author: {note.user.get_full_name() or note.user.username}  |  "
            f"Created: {note.created_at.strftime('%B %d, %Y')}  |  "
            f"Updated: {note.updated_at.strftime('%B %d, %Y')}")
    if note.category:
        meta += f"  |  Category: {note.category.name}"
    elements.append(Paragraph(meta, meta_style))

    if note.tags.exists():
        elements.append(Paragraph("Tags: " + ", ".join(f"#{t.name}" for t in note.tags.all()), meta_style))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=14))

    for line in note.content.split('\n'):
        elements.append(Paragraph(line, body_style) if line.strip() else Spacer(1, 8))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))
    elements.append(Paragraph("Exported from Mind Nest — Your AI Study Hub", footer_style))

    doc.build(elements)
    buffer.seek(0)

    filename = f"note_{note.pk}_{note.title[:30].replace(' ', '_')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_all_notes_pdf(request):
    notes  = Note.objects.filter(user=request.user).order_by('-is_pinned', '-updated_at')
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    cover_style      = ParagraphStyle('Cover',     parent=styles['Title'],    fontSize=28,
                                      textColor=colors.HexColor('#89b4fa'), alignment=TA_CENTER, spaceAfter=8)
    sub_style        = ParagraphStyle('Sub',       parent=styles['Normal'],   fontSize=12,
                                      textColor=colors.HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=4)
    note_title_style = ParagraphStyle('NoteTitle', parent=styles['Heading2'], fontSize=16,
                                      textColor=colors.HexColor('#1e1e2e'), spaceBefore=16, spaceAfter=6)
    meta_style       = ParagraphStyle('Meta',      parent=styles['Normal'],   fontSize=9,
                                      textColor=colors.HexColor('#64748b'), spaceAfter=8)
    body_style       = ParagraphStyle('Body',      parent=styles['Normal'],   fontSize=11,
                                      leading=18, spaceAfter=6)

    elements = [
        Spacer(1, 3*cm),
        Paragraph("Mind Nest", cover_style),
        Paragraph("All Notes Export", sub_style),
        Paragraph(f"{request.user.get_full_name() or request.user.username}  —  {notes.count()} notes", sub_style),
        Spacer(1, 1*cm),
        HRFlowable(width="80%", thickness=2, color=colors.HexColor('#89b4fa'), hAlign='CENTER'),
        Spacer(1, 3*cm),
    ]

    for note in notes:
        elements.append(Paragraph(note.title, note_title_style))
        meta = note.created_at.strftime('%B %d, %Y')
        if note.category:
            meta += f"  |  {note.category.name}"
        if note.is_pinned:
            meta += "  |  📌 Pinned"
        elements.append(Paragraph(meta, meta_style))
        for line in note.content.split('\n'):
            elements.append(Paragraph(line, body_style) if line.strip() else Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=0.5,
                                   color=colors.HexColor('#e2e8f0'), spaceAfter=10))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mind_nest_all_notes.pdf"'
    return response
