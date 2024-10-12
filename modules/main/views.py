from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile

# Create your views here.
@login_required(login_url='auth:login')
def main(request):
    user = request.user
    
    if not user.is_authenticated:
        return redirect('auth:login')
    
    user_profile = UserProfile.objects.get(user=user)
        
    image_url = f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'image_url': image_url,
        'show_navbar': True,
        'show_footer': True
    }
    
    return render(request, 'base.html', context)

def about(request):
    return render(request, 'about-us.html', {'show_navbar': True, 'show_footer': True})