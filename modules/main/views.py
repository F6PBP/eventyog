from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile

# Create your views here.
@check_user_profile(is_redirect=False)
def main(request):
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
    }
    
    return render(request, 'landing.html', context)

@check_user_profile(is_redirect=False)
def about(request):
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
    }
    return render(request, 'about-us.html', context)