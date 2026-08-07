from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('planner/', include('planner.urls')),
    path('notes/', include('notes.urls')),
    path('resources/', include('resources.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('', lambda request: redirect('dashboard:index'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
