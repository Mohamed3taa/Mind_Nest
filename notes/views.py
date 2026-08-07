from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def note_list(request):
    return render(request, 'notes/note_list.html')
