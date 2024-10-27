from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from django.contrib.auth.models import User
from modules.main.models import UserProfile
from django.http import HttpResponse
from django.core import serializers
from eventyog.types import AuthRequest
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from modules.authentication.forms import UserProfileForm
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate


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

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def see_user(request, user_id):
    if request.user_profile.role != 'AD':
        return redirect('main:home')
   
    # Debug
    print(f"Requested user_id: {user_id}")
    user = get_object_or_404(User, pk=user_id)
    print(f"Found user: {user.username}, ID: {user.id}")
    user_profile = get_object_or_404(UserProfile, user=user)
    print(f"Found profile: {user_profile.name}, User ID: {user_profile.user.id}")
    
    # Debug print to see what's in categories
    print(f"Raw categories: {user_profile.categories}")
    
    try:
        # Handle categories properly
        categories = []
        if user_profile.categories:
            # Strip any whitespace and split only if there's content
            categories = [cat.strip() for cat in user_profile.categories.split(',') if cat.strip()]
        
        print(f"Processed categories: {categories}")  # Debug print
        
        context = {
            'user': user,
            'user_profile': user_profile,
            'image_url': user_profile.profile_picture.url if user_profile.profile_picture else None,
            'categories': categories,
            'show_navbar': True,
            'show_footer': True,
            'is_admin': True,
        }
        return render(request, 'user.html', context)
   
    except Exception as e:
        print(f"Error: {str(e)}")
        print('User profile not found.')
        return redirect('auth:onboarding')

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def edit_user(request, user_id):
    if request.user_profile.role != 'AD':
        return redirect('main:home')
       
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        # Debug prints
        print("POST data received:", request.POST)
        print("Categories from POST:", request.POST.get('categories'))
        
        # Update user profile
        user_profile.name = request.POST.get('name')
        user_profile.bio = request.POST.get('bio')
        user_profile.email = request.POST.get('email')
        user_profile.wallet = request.POST.get('wallet')
        
        # Handle categories with debug logging
        categories = request.POST.get('categories', '')
        print("Categories before save:", categories)
        user_profile.categories = categories
        
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            
        user_profile.save()
        print("Categories after save:", user_profile.categories)
        
        # Update username
        user.username = request.POST.get('username')
        user.save()
        
        messages.success(request, 'User profile updated successfully')
        return redirect('admin_dashboard:see_user', user_id=user.id)


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

@login_required(login_url='auth:login')
def create_user(request):
    user_form = UserCreationForm()
    profile_form = UserProfileForm()
    
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save the new user
            user = user_form.save()
            messages.success(request, 'Account created successfully.')
            
            # Save the user profile
            profile = profile_form.save(commit=False)
            profile.user = user  # Associate profile with the new user
            profile.save()
            
            return redirect('admin_dashboard:main')
        else:
            # Handle errors for user form or profile form
            if not user_form.is_valid():
                messages.error(request, 'Error creating account: User form is not valid')
                return redirect('admin_dashboard:main')
            if not profile_form.is_valid():
                messages.error(request, 'Error creating account: Profile form is not valid')
                return redirect('admin_dashboard:main')
    
    context = {
    'user_form': user_form,
    'profile_form': profile_form,
    'show_navbar': True,
    'show_footer': True,
}
    return render(request, 'users.html', context)
