from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def resource_list(request):
    return render(request, 'resources/resource_list.html')
