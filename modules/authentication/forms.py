from django import forms
from modules.main.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'bio', 'profile_picture', 'categories']
        
    def save(self, commit=True):
        user_profile = super().save(commit=False)
        
        if not self.cleaned_data.get('profile_picture'):
            print('No profile picture uploaded.')
            
        if commit:
            user_profile.save()
        
        return user_profile