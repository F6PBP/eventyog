from django import forms
from modules.main.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'bio', 'profile_picture', 'categories']
        
    def save(self, commit=True):
        user_profile = super().save(commit=False)
        if self.cleaned_data.get('profile_picture'):
            user_profile.profile_picture = self.cleaned_data['profile_picture']
        if commit:
            user_profile.save()
        return user_profile