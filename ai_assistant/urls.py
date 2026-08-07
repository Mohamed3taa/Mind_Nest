from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('',                          views.chat,               name='chat'),
    path('new/',                      views.new_conversation,   name='new_conversation'),
    path('<int:conv_id>/send/',        views.send_message,       name='send_message'),
    path('<int:conv_id>/delete/',      views.delete_conversation, name='delete_conversation'),
]
