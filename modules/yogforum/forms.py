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

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Forum  # Default to Forum; override dynamically if editing a reply
        fields = ['content']  # Allow editing content only

    def __init__(self, *args, **kwargs):
        # Dynamically set the model based on the instance provided
        if 'instance' in kwargs and isinstance(kwargs['instance'], ForumReply):
            self._meta.model = ForumReply  # Use ForumReply if the instance is a reply
        super(EditPostForm, self).__init__(*args, **kwargs)