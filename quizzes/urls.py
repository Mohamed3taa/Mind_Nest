from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Step 2 — AI generation + saving
    path('generate/',                          views.quiz_generate, name='quiz_generate'),
    path('save/',                              views.quiz_save,     name='quiz_save'),

    # Step 3 — list + detail + delete
    path('',                                   views.quiz_list,     name='quiz_list'),
    path('<int:pk>/',                          views.quiz_detail,   name='quiz_detail'),
    path('<int:pk>/delete/',                   views.quiz_delete,   name='quiz_delete'),

    # Step 4 — take + submit
    path('<int:pk>/take/',                     views.quiz_take,     name='quiz_take'),
    path('<int:pk>/submit/',                   views.quiz_submit,   name='quiz_submit'),

    # Step 5 — result
    path('<int:pk>/result/<int:attempt_pk>/',  views.quiz_result,   name='quiz_result'),
]
