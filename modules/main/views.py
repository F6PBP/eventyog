from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile

# Create your views here.
@login_required(login_url='auth:login')
@check_user_profile
def main(request):
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
    }
    
    return render(request, 'landing.html', context)

@check_user_profile
def about(request):
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
    }
    return render(request, 'about-us.html', context)