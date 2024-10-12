# your_app/decorators.py
from django.shortcuts import redirect
from modules.main.models import UserProfile

def check_user_profile(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('auth:login')

        image_url = None
        try:
            user_profile = UserProfile.objects.get(user=user)
            image_url = f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
            request.image_url = image_url
            request.user_profile = user_profile
        except UserProfile.DoesNotExist:
            return redirect('auth:onboarding')

        return view_func(request, *args, **kwargs)
    
    return wrapper
