from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from modules.main.models import UserProfile
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from eventyog.types import AuthRequest

import datetime

from .forms import UserProfileForm

# Create your views here.
def login_user(request: AuthRequest):
    if (request.user.is_authenticated):return redirect('main:main')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse('main:main'))
            response.set_cookie('last_login', datetime.datetime.now())
            return response
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm(request)

    context = {'form': form, 'show_navbar': False, 'show_footer': False}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('auth:login'))
    response.delete_cookie('last_login')
    return response

def register(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            
            # Authenticate the newly registered user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            # Log in the user
            if user is not None:
                login(request, user)  # Automatically log in the user
            
            return redirect('auth:onboarding')
        
    context = {
        'form': form
    }
    
    return render(request, 'register.html', context)

def onboarding(request):
    # Check if user has profile
    if (request.user.is_authenticated == False):
        return redirect('auth:login')
    
    profile = UserProfile.objects.filter(user=request.user)
    if (len(profile) > 0):
        print('User has profile')
        print(profile)
        return redirect('main:main')
    elif (len(profile) == 0):
        print('User does not have profile')
        
    if request.method == 'POST':
        # Process the form data here
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate profile with logged-in user
            profile.save()
            return redirect('main:main')
        else:
            messages.error(request, 'Please pick a profile picture')
            print(form.errors)
    else:
        form = UserProfileForm()

    context = {
        'form': form
    }
    
    return render(request, 'onboarding.html', context)

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def profile(request):
    try:
        if (request.user_profile.categories == '' or request.user_profile.categories == None):
            categories = None
        else:
            categories = request.user_profile.categories.split(',')
            
        context = {
            'user': request.user,
            'user_profile': request.user_profile,
            'image_url': request.image_url,
            'show_navbar': True,
            'show_footer': True,
            'categories': categories
        }
        
        return render(request, 'profile.html', context)

    except Exception as e:
        print(e)
        print('User profile not found.')
        return redirect('auth:onboarding')

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def edit_profile(request):
    form = UserProfileForm(instance=request.user_profile)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate profile with logged-in user
            
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
                        
            return redirect('auth:profile')
        else:
            print("HELLO 2")
            print(form.errors)
            print(form.data)
            
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'categories': request.user_profile.categories,
        'form': form,
        'show_navbar': True,
        'show_footer': True
    }

    return render(request, 'edit_profile.html', context)

def delete_profile(request):
    try:
        if request.method == 'POST':
            request.user_profile.delete()
            request.user.delete()
            print('Profile deleted successfully.')
            logout(request)
            response = HttpResponseRedirect(reverse('auth:login'))
            response.delete_cookie('last_login')
            messages.success(request, 'Profile deleted successfully.')
            return response
    except Exception as e:
        print(e)
        request.user.delete()
        logout(request)
        response = HttpResponseRedirect(reverse('auth:login'))
        response.delete_cookie('last_login')
        return redirect('auth:login')
        
    print("TETSSS")
    return redirect('auth:login')