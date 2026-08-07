from django import forms
from .models import Note, Category, Tag


class CategoryForm(forms.ModelForm):
    class Meta:
        model   = Category
        fields  = ('name', 'color')
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name...'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }


class NoteForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Add tags separated by commas...'
        })
    )

    class Meta:
        model   = Note
        fields  = ('title', 'content', 'category', 'is_pinned')
        widgets = {
            'title':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note title...'}),
            'content':   forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Write your note here...'}),
            'category':  forms.Select(attrs={'class': 'form-select'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['category'].empty_label = 'No Category'
            # pre-fill tags_input if editing
            if self.instance.pk:
                self.fields['tags_input'].initial = ', '.join(
                    self.instance.tags.values_list('name', flat=True)
                )
