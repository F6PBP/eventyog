from  django.http import HttpRequest, JsonResponse
from modules.api.ApiResponse import ApiResponse
import json

def main(request: HttpRequest) -> ApiResponse:
    return ApiResponse(status=200, content="Hello, World!")

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from django.contrib.auth.models import User
from modules.main.models import UserProfile
from django.core import serializers
from eventyog.types import AuthRequest
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from modules.authentication.forms import UserProfileForm
from django.contrib.auth import login, logout, authenticate

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def show_main(request: AuthRequest) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)
    
    user_profiles = UserProfile.objects.values('id', 'name', 'role', 'email')
    return JsonResponse({
        "status": True,
        "message": "Admin data retrieved successfully.",
        "data": list(user_profiles)
    }, status=200)


@login_required(login_url='auth:login')
def search_users(request: AuthRequest) -> JsonResponse:
    search = request.GET.get('search', '')
    users = UserProfile.objects.filter(name__icontains=search).values('id', 'name', 'email', 'role')
    return JsonResponse({
        "status": True,
        "message": "Users retrieved successfully.",
        "data": list(users)
    }, status=200)

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def see_user(request, user_id) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)
    
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    categories = user_profile.categories.split(',') if user_profile.categories else []
    
    return JsonResponse({
        "status": True,
        "message": "User profile retrieved successfully.",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user_profile.email,
            "bio": user_profile.bio,
            "categories": categories
        }
    }, status=200)


@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def edit_user(request, user_id) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)
    
    user = get_object_or_404(User, pk=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        user_profile.name = data.get('name', user_profile.name)
        user_profile.bio = data.get('bio', user_profile.bio)
        user_profile.email = data.get('email', user_profile.email)
        user_profile.wallet = data.get('wallet', user_profile.wallet)
        user_profile.categories = ','.join(data.get('categories', []))
        
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        
        user_profile.save()
        user.username = data.get('username', user.username)
        user.save()
        
        return JsonResponse({"status": True, "message": "User profile updated successfully."}, status=200)
    
    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def delete_user(request, user_id):
    if request.user_profile.role != 'AD':
        return JsonResponse({
            "status": False,
            "message": "You do not have permission to perform this action."
        }, status=403)
        
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, pk=user_id)
            user.delete()
            return JsonResponse({
                "status": True,
                "message": "User account deleted successfully."
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"An error occurred: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method. Only POST is allowed."
    }, status=400)

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def create_user(request) -> JsonResponse:
    if request.method == 'POST':
        data = json.loads(request.body)
        user_form = UserCreationForm(data)
        profile_form = UserProfileForm(data)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            return JsonResponse({"status": True, "message": "User created successfully."}, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Invalid form data.",
                "errors": {
                    "user_form": user_form.errors,
                    "profile_form": profile_form.errors
                }
            }, status=400)
    
    return JsonResponse({"status": False, "message": "Invalid request method."}, status=405)
