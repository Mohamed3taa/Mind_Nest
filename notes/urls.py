from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('',                        views.note_list,        name='note_list'),
    path('<int:pk>/',               views.note_detail,      name='note_detail'),
    path('create/',                 views.note_create,      name='note_create'),
    path('<int:pk>/edit/',          views.note_edit,        name='note_edit'),
    path('<int:pk>/delete/',        views.note_delete,      name='note_delete'),
    path('<int:pk>/pin/',           views.note_toggle_pin,  name='note_toggle_pin'),
    path('category/create/',        views.category_create,  name='category_create'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
