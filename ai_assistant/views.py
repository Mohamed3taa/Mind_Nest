import os
import json
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import AIConversation, AIMessage, UploadedDocument

client = genai.Client(api_key=os.getenv('AI_API_KEY'))


def extract_text_from_file(file, doc_type):
    try:
        if doc_type == 'pdf':
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            return ''.join([page.extract_text() or '' for page in reader.pages]).strip()
        elif doc_type == 'docx':
            from docx import Document
            doc = Document(file)
            return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        elif doc_type == 'txt':
            return file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[EXTRACT ERROR] {e}")
    return ''


def build_user_context(user):
    from notes.models import Note
    from planner.models import Task
    from resources.models import Resource

    context_parts = []

    documents = UploadedDocument.objects.filter(user=user)
    if documents.exists():
        context_parts.append("=== USER'S UPLOADED DOCUMENTS ===")
        for doc in documents:
            context_parts.append(f"Document: {doc.title} ({doc.doc_type.upper()})")
            if doc.extracted_text:
                context_parts.append(doc.extracted_text[:3000])

    notes = Note.objects.filter(user=user).order_by('-updated_at')[:20]
    if notes.exists():
        context_parts.append("=== USER'S NOTES ===")
        for note in notes:
            note_text = f"Title: {note.title}\n"
            if note.category:
                note_text += f"Category: {note.category.name}\n"
            tags = note.tags.values_list('name', flat=True)
            if tags:
                note_text += f"Tags: {', '.join(tags)}\n"
            note_text += f"Content:\n{note.content}\n"
            context_parts.append(note_text)

    tasks = Task.objects.filter(user=user).order_by('-created_at')[:20]
    if tasks.exists():
        context_parts.append("=== USER'S STUDY TASKS ===")
        for task in tasks:
            task_text = f"- {task.title} | Priority: {task.priority} | Status: {task.status}"
            if task.due_date:
                task_text += f" | Due: {task.due_date}"
            if task.description:
                task_text += f"\n  Description: {task.description}"
            context_parts.append(task_text)

    resources = Resource.objects.filter(user=user).order_by('-created_at')[:20]
    if resources.exists():
        context_parts.append("=== USER'S LEARNING RESOURCES ===")
        for res in resources:
            res_text = f"- {res.title}"
            if res.resource_type:
                res_text += f" [{res.resource_type.name}]"
            if res.description:
                res_text += f": {res.description}"
            res_text += f" | Link: {res.link}"
            context_parts.append(res_text)

    if not context_parts:
        return "The user has no data yet in Mind Nest."

    return "\n".join(context_parts)


def get_system_prompt(user):
    user_data = build_user_context(user)

    return f"""You are Mind Nest AI, a personal study assistant for {user.get_full_name() or user.username}.

IMPORTANT RULES:
1. You ONLY answer based on the user's data provided below (notes, tasks, resources, uploaded documents).
2. If the user asks about something NOT in their data, say: "I don't find this in your Mind Nest data. Please add related notes, resources, or upload a document first."
3. You can help the user:
   - Summarize or explain their notes and uploaded documents
   - Generate quiz questions FROM their notes/documents
   - Create flashcards FROM their notes/documents
   - Review their tasks and suggest priorities
   - Answer questions about their saved resources
4. Do NOT act as a general knowledge chatbot.
5. Be concise, friendly, and educational.

HERE IS THE USER'S DATA:
{user_data}

Answer only based on the data above."""


def get_gemini_response(conversation_history, user_message, user):
    try:
        contents = []
        for msg in conversation_history:
            role = 'user' if msg.role == 'user' else 'model'
            contents.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))

        contents.append(types.Content(role='user', parts=[types.Part(text=user_message)]))

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=get_system_prompt(user))
        )
        return response.text

    except Exception as e:
        print(f"[AI ERROR] {type(e).__name__}: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


@login_required
def chat(request):
    conversations = AIConversation.objects.filter(user=request.user)
    active_conv   = None
    messages_list = []
    documents     = UploadedDocument.objects.filter(user=request.user)

    conv_id = request.GET.get('conv')
    if conv_id:
        active_conv   = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
        messages_list = active_conv.messages.all()

    from notes.models import Note
    from planner.models import Task
    from resources.models import Resource

    context = {
        'conversations':   conversations,
        'active_conv':     active_conv,
        'messages_list':   messages_list,
        'documents':       documents,
        'notes_count':     Note.objects.filter(user=request.user).count(),
        'tasks_count':     Task.objects.filter(user=request.user).count(),
        'resources_count': Resource.objects.filter(user=request.user).count(),
        'docs_count':      documents.count(),
    }
    return render(request, 'ai_assistant/chat.html', context)


@login_required
def new_conversation(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'New Conversation')
        conv  = AIConversation.objects.create(user=request.user, title=title)
        return redirect(f'/ai/?conv={conv.pk}')
    return redirect('ai_assistant:chat')


@login_required
@require_POST
def send_message(request, conv_id):
    conv     = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    data     = json.loads(request.body)
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    AIMessage.objects.create(conversation=conv, role='user', content=user_msg)

    history = list(conv.messages.all().order_by('created_at'))
    history = history[:-1][-10:]

    ai_response = get_gemini_response(history, user_msg, request.user)

    AIMessage.objects.create(conversation=conv, role='assistant', content=ai_response)

    if conv.messages.count() == 2 and conv.title == 'New Conversation':
        conv.title = user_msg[:50]
        conv.save()

    return JsonResponse({'response': ai_response, 'conv_title': conv.title})


@login_required
def upload_document(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')
        title         = request.POST.get('title', '').strip()

        if not uploaded_file:
            messages.error(request, 'Please select a file.')
            return redirect('ai_assistant:chat')

        filename = uploaded_file.name.lower()
        if filename.endswith('.pdf'):
            doc_type = 'pdf'
        elif filename.endswith('.docx'):
            doc_type = 'docx'
        elif filename.endswith('.txt'):
            doc_type = 'txt'
        else:
            messages.error(request, 'Only PDF, DOCX, and TXT files are supported.')
            return redirect('ai_assistant:chat')

        if not title:
            title = uploaded_file.name

        extracted_text = extract_text_from_file(uploaded_file, doc_type)
        uploaded_file.seek(0)

        UploadedDocument.objects.create(
            user=request.user,
            title=title,
            file=uploaded_file,
            doc_type=doc_type,
            extracted_text=extracted_text
        )
        messages.success(request, f'"{title}" uploaded and ready for AI analysis!')

    return redirect('ai_assistant:chat')


@login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(UploadedDocument, pk=doc_id, user=request.user)
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Document deleted.')
    return redirect('ai_assistant:chat')


@login_required
def delete_conversation(request, conv_id):
    conv = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    if request.method == 'POST':
        conv.delete()
        messages.success(request, 'Conversation deleted.')
    return redirect('ai_assistant:chat')
