"""
ai_assistant/views.py
----------------------
Handles the AI chat interface using Google Gemini API.
The AI answers ONLY based on the user's own data in Mind Nest:
- Their notes, categories, tags
- Their tasks (planner)
- Their saved resources
This makes it a personal study assistant, not a general chatbot.
"""

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
from .models import AIConversation, AIMessage

# Initialize Gemini client once at module level
client = genai.Client(api_key=os.getenv('AI_API_KEY'))


def build_user_context(user):
    """
    Build a context string from the user's actual data in Mind Nest.
    This is injected into the system prompt so Gemini only answers
    based on what the user has stored.

    Returns:
        str: formatted context string with user's notes, tasks, resources
    """
    from notes.models import Note
    from planner.models import Task
    from resources.models import Resource

    context_parts = []

    # ── User's Notes ────────────────────────────────────────────
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

    # ── User's Tasks ────────────────────────────────────────────
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

    # ── User's Resources ────────────────────────────────────────
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
        return "The user has no data yet in Mind Nest (no notes, tasks, or resources)."

    return "\n".join(context_parts)


def get_system_prompt(user):
    """
    Build a dynamic system prompt that includes the user's actual data.
    Gemini will only answer based on this data.
    """
    user_data = build_user_context(user)

    return f"""You are Mind Nest AI, a personal study assistant for {user.get_full_name() or user.username}.

IMPORTANT RULES:
1. You ONLY answer based on the user's data provided below.
2. If the user asks about something NOT in their data, say: "I don't find this in your Mind Nest data. Please add related notes or resources first."
3. You can help the user:
   - Summarize or explain their notes
   - Generate quiz questions FROM their notes
   - Create flashcards FROM their notes
   - Review their tasks and suggest priorities
   - Explain concepts mentioned in their notes
   - Answer questions about their saved resources
4. Do NOT act as a general knowledge chatbot.
5. Be concise, friendly, and educational.

HERE IS THE USER'S DATA:
{user_data}

Answer only based on the data above."""


def get_gemini_response(conversation_history, user_message, user):
    """
    Send a message to Gemini with the user's personal data as context.

    Args:
        conversation_history: list of AIMessage objects (previous messages)
        user_message: the new user message string
        user: the Django User object (to fetch their data)

    Returns:
        str: AI response based on user's data only
    """
    try:
        # Build contents list from conversation history
        contents = []
        for msg in conversation_history:
            role = 'user' if msg.role == 'user' else 'model'
            contents.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))

        # Append the new user message
        contents.append(types.Content(role='user', parts=[types.Part(text=user_message)]))

        # Build system prompt with user's actual data
        system_prompt = get_system_prompt(user)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt)
        )
        return response.text

    except Exception as e:
        print(f"[AI ERROR] {type(e).__name__}: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


@login_required
def chat(request):
    """
    Main chat page. Shows conversation list on the left
    and the active conversation messages on the right.
    """
    conversations = AIConversation.objects.filter(user=request.user)
    active_conv   = None
    messages_list = []

    conv_id = request.GET.get('conv')
    if conv_id:
        active_conv   = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
        messages_list = active_conv.messages.all()

    # Count user's data for display
    from notes.models import Note
    from planner.models import Task
    from resources.models import Resource

    context = {
        'conversations':  conversations,
        'active_conv':    active_conv,
        'messages_list':  messages_list,
        'notes_count':    Note.objects.filter(user=request.user).count(),
        'tasks_count':    Task.objects.filter(user=request.user).count(),
        'resources_count': Resource.objects.filter(user=request.user).count(),
    }
    return render(request, 'ai_assistant/chat.html', context)


@login_required
def new_conversation(request):
    """Create a new conversation and redirect to it."""
    if request.method == 'POST':
        title = request.POST.get('title', 'New Conversation')
        conv  = AIConversation.objects.create(user=request.user, title=title)
        return redirect(f'/ai/?conv={conv.pk}')
    return redirect('ai_assistant:chat')


@login_required
@require_POST
def send_message(request, conv_id):
    """
    Handle AJAX message send.
    Injects user's notes, tasks, and resources into system prompt
    so Gemini only answers based on the user's own data.
    """
    conv     = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    data     = json.loads(request.body)
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save user message
    AIMessage.objects.create(conversation=conv, role='user', content=user_msg)

    # Get history excluding current message
    history = list(conv.messages.all().order_by('created_at'))
    history = history[:-1][-10:]

    # Get AI response — passing user object to build context from their data
    ai_response = get_gemini_response(history, user_msg, request.user)

    # Save AI response
    AIMessage.objects.create(conversation=conv, role='assistant', content=ai_response)

    # Auto-set conversation title
    if conv.messages.count() == 2 and conv.title == 'New Conversation':
        conv.title = user_msg[:50]
        conv.save()

    return JsonResponse({
        'response':   ai_response,
        'conv_title': conv.title,
    })


@login_required
def delete_conversation(request, conv_id):
    """Delete a conversation and all its messages."""
    conv = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    if request.method == 'POST':
        conv.delete()
        messages.success(request, 'Conversation deleted.')
    return redirect('ai_assistant:chat')
