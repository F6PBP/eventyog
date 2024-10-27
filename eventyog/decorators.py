# your_app/decorators.py
from functools import wraps
from django.shortcuts import redirect
from modules.main.models import UserProfile

def check_user_profile(is_redirect=True):
    def check_redirect(view_func):
        @wraps(view_func)  # Preserve metadata of the view function
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Initialize request attributes
            request.image_url = None
            request.user_profile = None
            request.role = None
            request.is_admin = False

            # Redirect to login if not authenticated
            if not user.is_authenticated and is_redirect:
                return redirect('auth:login')

            try:
                # Retrieve user profile information
                user_profile = UserProfile.objects.get(user=user)
                image_url = (
                    f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
                    if user_profile.profile_picture
                    else 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
                )

                # Set request attributes based on user profile
                request.image_url = image_url
                request.user_profile = user_profile
                request.role = user_profile.role
                request.is_admin = user_profile.role == 'AD'
            except UserProfile.DoesNotExist:
                return redirect('auth:onboarding')
            except Exception as e:
                print('Error in check_user_profile:', e)
                
            # Call the original view function with all arguments
            return view_func(request, *args, **kwargs)

        return wrapper
    return check_redirect
