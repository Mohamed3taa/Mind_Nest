from django import forms
from .models import Resource, ResourceType


class ResourceForm(forms.ModelForm):
    class Meta:
        model   = Resource
        fields  = ('title', 'description', 'link', 'resource_type', 'is_favorite')
        widgets = {
            'title':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource title...'}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short description...'}),
            'link':          forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'is_favorite':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resource_type'].empty_label = 'Select Type'
        self.fields['resource_type'].required    = False
