from django import forms
from modules.main.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'bio', 'profile_picture', 'categories']