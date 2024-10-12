from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from modules.main.models import UserProfile
import datetime

from .forms import UserProfileForm

# Create your views here.
def login_user(request):
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
    print(request.user)
    
    if not request.user.is_authenticated:
        return redirect('auth:login')    
    
    profile = UserProfile.objects.filter(user=request.user)
    
    if profile:
        return redirect('main:main')
    
    if request.method == 'POST':
        # Process the form data here
        form = UserProfileForm(request.POST, request.FILES)
        print(form.data)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate profile with logged-in user
            profile.save()
            return redirect('main:main')
        else:
            print(form.errors)
    else:
        form = UserProfileForm()

    context = {
        'form': form
    }
    
    print(context)
    
    return render(request, 'onboarding.html', context)

def profile(request):
    user = request.user
    
    context = {
        'user': user
    }
    
    return render(request, 'profile.html', context)

def edit_profile(request):
    pass