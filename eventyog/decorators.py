# your_app/decorators.py
from django.shortcuts import redirect
from modules.main.models import UserProfile

def check_user_profile(is_redirect = True):
    def check_redirect(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            request.image_url = None
            request.user_profile = None
            request.role = None
            request.is_admin = False

            if not user.is_authenticated and is_redirect:
                return redirect('auth:login')

            image_url = None
            try:
                user_profile = UserProfile.objects.get(user=user)
                print(user_profile)
                if (user_profile.profile_picture):
                    image_url = f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
                else:
                    image_url = 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
                request.image_url = image_url
                request.user_profile = user_profile
                request.role = user_profile.role
                request.is_admin = user_profile.role == 'AD'
            except UserProfile.DoesNotExist:
                return redirect('auth:onboarding')
            except Exception as e:
                print(e)
                
            return view_func(request, *args, **kwargs)
        
        return wrapper

    return check_redirect
