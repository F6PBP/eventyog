from django import forms
from modules.main.models import Forum, ForumReply

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

class AddReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']  # Assuming 'content' is the field where the reply content is stored

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your reply...',
                'rows': 4,
            }),
        }

        labels = {
            'content': 'Your Reply',
        }