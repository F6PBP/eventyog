from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from django.contrib.auth.models import User
from modules.main.models import UserProfile
from django.http import HttpResponse
from django.core import serializers
from eventyog.types import AuthRequest
from django.contrib import messages


# Create your views here.
@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def show_main(request: AuthRequest) -> HttpResponse:
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
def search_users(request: AuthRequest) -> HttpResponse:
    search = request.GET.get('search', '')
    users = UserProfile.objects.filter(name__contains=search)
    
    data = serializers.serialize('json', users)
    
    return HttpResponse(data, content_type='application/json')

'''
def see_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    user_profile = UserProfile.objects.get(user=user)
    
    context = {
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture.url,
        'show_navbar': True,
        'show_footer': True,
    }

    return render(request, 'user.html', context)
'''

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def see_user(request, user_id):
    if request.user_profile.role != 'AD':
        return redirect('main:home')
    
    print(f"Requested user_id: {user_id}")
    user = get_object_or_404(User, pk=user_id)
    print(f"Found user: {user.username}, ID: {user.id}")
    user_profile = get_object_or_404(UserProfile, user=user)
    print(f"Found profile: {user_profile.name}, User ID: {user_profile.user.id}")
        
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture.url if user_profile.profile_picture else None,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': True,
    }

    return render(request, 'user.html', context)

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def edit_user(request, user_id):
    if request.user_profile.role != 'AD':
        return redirect('main:home')
        
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture.url if user_profile.profile_picture else None,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': True,
    }

    if request.method == 'POST':
        # Update user profile
        user_profile.name = request.POST.get('name')
        user_profile.bio = request.POST.get('bio')
        
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']

        categories = request.POST.get('categories')
        user_profile.categories = categories
            
        user_profile.save()
        
        # Update user email
        user.email = request.POST.get('email')
        user.save()

        messages.success(request, 'User profile updated successfully')
        
        # Render the same page with updated data and success message
        return render(request, 'user.html', context)
    
    # For GET request, render the edit page with current context
    return render(request, 'user.html', context)


@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def delete_user(request, user_id):
    if request.user_profile.role != 'AD':
        return redirect('main:home')
        
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        messages.success(request, 'User account deleted successfully')
        return redirect('admin_dashboard:main')  # Change this line to use the correct namespaced URL
        
    return redirect('admin_dashboard:see_user', user_id=user_id)  # Also use the namespaced URL here
