from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib import messages
import datetime

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
            
            return redirect('auth:login')
        
    context = {
        'form': form
    }
    
    return render(request, 'register.html', context)

def profile(request):
    user = request.user
    
    context = {
        'user': user
    }
    
    return render(request, 'profile.html', context)

def edit_profile(request):
    pass