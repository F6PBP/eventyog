from django import forms
from modules.main.models import Forum

class AddForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ['title', 'content']  # Field yang akan diisi oleh user

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title',
                'required': 'required',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post content',
                'rows': 5,
                'required': 'required',
            }),
        }
