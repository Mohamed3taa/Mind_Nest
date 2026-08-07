import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import AIConversation, AIMessage

# Configure Gemini client
client = genai.Client(api_key=os.getenv('AI_API_KEY'))


def get_gemini_response(conversation_history, user_message):
    """Send message to Gemini and get response"""
    try:
        # Build history for context
        history = []
        for msg in conversation_history:
            role = 'user' if msg.role == 'user' else 'model'
            history.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))

        # Add current user message
        history.append(types.Content(role='user', parts=[types.Part(text=user_message)]))

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Mind Nest AI, a helpful study assistant. "
                    "You help students with their studies, explain concepts, "
                    "summarize notes, generate quiz questions, and answer programming questions. "
                    "Be concise, friendly, and educational."
                )
            )
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
    if request.method == 'POST':
        title = request.POST.get('title', 'New Conversation')
        conv  = AIConversation.objects.create(user=request.user, title=title)
        return redirect(f"{request.path_info.replace('new/', '')}?conv={conv.pk}")
    return redirect('ai_assistant:chat')


@login_required
@require_POST
def send_message(request, conv_id):
    """Handle message send — returns JSON"""
    conv    = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    data    = json.loads(request.body)
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save user message
    AIMessage.objects.create(conversation=conv, role='user', content=user_msg)

    # Get conversation history (all messages except the one just saved, last 10 for context)
    history = list(conv.messages.all().order_by('created_at'))
    # exclude last message (the one just saved) to avoid duplication
    history = history[:-1][-10:]

    # Get AI response
    ai_response = get_gemini_response(history, user_msg)

    # Save AI message
    ai_msg = AIMessage.objects.create(conversation=conv, role='assistant', content=ai_response)

    # Update conversation title if it's the first message
    if conv.messages.count() == 2 and conv.title == 'New Conversation':
        conv.title = user_msg[:50]
        conv.save()

    return JsonResponse({
        'response':  ai_response,
        'conv_title': conv.title,
    })


@login_required
def delete_conversation(request, conv_id):
    conv = get_object_or_404(AIConversation, pk=conv_id, user=request.user)
    if request.method == 'POST':
        conv.delete()
        messages.success(request, 'Conversation deleted.')
    return redirect('ai_assistant:chat')
