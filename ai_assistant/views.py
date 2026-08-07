"""
ai_assistant/views.py
----------------------
Handles the AI chat interface using Google Gemini API.
Features:
- Multiple conversations per user
- Persistent message history
- Context-aware responses (last 10 messages sent as history)
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

# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "You are Mind Nest AI, a helpful study assistant. "
    "You help students with their studies, explain concepts, "
    "summarize notes, generate quiz questions, and answer programming questions. "
    "Be concise, friendly, and educational."
)


def get_gemini_response(conversation_history, user_message):
    """
    Send a message to Gemini and return the AI response text.

    Args:
        conversation_history: list of AIMessage objects (previous messages)
        user_message: the new user message string

    Returns:
        str: AI response text, or error message on failure
    """
    try:
        # Build contents list from conversation history
        contents = []
        for msg in conversation_history:
            role = 'user' if msg.role == 'user' else 'model'
            contents.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))

        # Append the new user message
        contents.append(types.Content(role='user', parts=[types.Part(text=user_message)]))

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
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
    Active conversation is selected via ?conv=<id> query param.
    """
    conversations = AIConversation.objects.filter(user=request.user)
    active_conv   = None
    messages_list = []

    conv_id = request.GET.get('conv')
    if conv_id:
        active_conv   = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
        messages_list = active_conv.messages.all()

    context = {
        'conversations': conversations,
        'active_conv':   active_conv,
        'messages_list': messages_list,
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
    - Saves user message to DB
    - Fetches last 10 messages as context
    - Calls Gemini API
    - Saves AI response to DB
    - Auto-updates conversation title from first message
    Returns: JSON with 'response' and 'conv_title'
    """
    conv     = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    data     = json.loads(request.body)
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save user message first
    AIMessage.objects.create(conversation=conv, role='user', content=user_msg)

    # Get history excluding the message just saved (avoid duplication)
    history = list(conv.messages.all().order_by('created_at'))
    history = history[:-1][-10:]   # last 10 messages before current

    # Get AI response from Gemini
    ai_response = get_gemini_response(history, user_msg)

    # Save AI response
    AIMessage.objects.create(conversation=conv, role='assistant', content=ai_response)

    # Auto-set conversation title from first user message
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
