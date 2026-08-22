from django import forms
from django.utils import timezone
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
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title...', 'maxlength': '200'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optional)...'}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
            'status':      forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            today = timezone.now().date()
            # Only validate on NEW tasks (no pk yet) — allow past dates on edit
            if not self.instance.pk and due_date < today:
                raise forms.ValidationError('Due date cannot be in the past.')
        return due_date
