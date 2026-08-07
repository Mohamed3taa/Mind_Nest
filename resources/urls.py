from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('',                       views.resource_list,             name='resource_list'),
    path('create/',                views.resource_create,           name='resource_create'),
    path('<int:pk>/edit/',         views.resource_edit,             name='resource_edit'),
    path('<int:pk>/delete/',       views.resource_delete,           name='resource_delete'),
    path('<int:pk>/favorite/',     views.resource_toggle_favorite,  name='resource_toggle_favorite'),
]
