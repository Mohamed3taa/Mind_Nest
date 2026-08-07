from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model   = Task
        fields  = ('title', 'description', 'priority', 'status', 'due_date')
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optional)...'}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
            'status':      forms.Select(attrs={'class': 'form-select'}),
        }
