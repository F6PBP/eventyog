from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from django.contrib.auth.models import User
from modules.main.models import UserProfile
from django.http import HttpResponse
from django.core import serializers


# Create your views here.
@login_required(login_url='auth:login')
@check_user_profile
def show_main(request):
    user_profiles = UserProfile.objects.all()
    
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
        'users': user_profiles,
    }
    
    
    return render(request, 'users.html', context)

@login_required(login_url='auth:login')
def search_users(request):
    search = request.GET.get('search', '')
    users = UserProfile.objects.filter(name__contains=search)
    
    data = serializers.serialize('json', users)
    
    return HttpResponse(data, content_type='application/json')

def see_user(request, user_id):
    user = User.objects.get(id=user_id)
    
    user_profile = UserProfile.objects.filter(user=user)
    
    context = {
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture.url,
        'show_navbar': True,
        'show_footer': True,
    }
    
    return render(request, 'user.html', context)