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
from django.http import JsonResponse

#@login_required(login_url='auth:login')
#@check_user_profile(is_redirect=False)
def show_main(request: AuthRequest) -> JsonResponse:
    #if request.user_profile.role != 'AD':
        #return JsonResponse({"status": False, "message": "Access denied."}, status=403)

    # Fetch user profiles
    user_profiles = UserProfile.objects.values('id', 'user', 'name', 'role', 'email', 'bio', 'categories')
    
    # Fetch usernames and date_joined along with user ids
    user_details = User.objects.values('username', 'id', 'date_joined')  # Fetch both username and date_joined

    # Convert user details to a dictionary for easy access by user id
    user_dict = {user['id']: {'username': user['username'], 'date_joined': user['date_joined']} for user in user_details}

    # Now, we merge the username and date_joined into the user profile data
    merged_profiles = []
    for profile in user_profiles:
        user_id = profile['user']
        user_info = user_dict.get(user_id, {'username': '', 'date_joined': None})  # Default values if no match found
        
        # Add the username and date_joined to the profile data
        profile['username'] = user_info['username']
        profile['date_joined'] = user_info['date_joined']
        merged_profiles.append(profile)

    return JsonResponse({
        "status": True,
        "message": "Admin data retrieved successfully.",
        "data": merged_profiles
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

#@login_required(login_url='auth:login')
#@check_user_profile(is_redirect=True)
def see_user(request, username) -> JsonResponse:
    try:
        # user = get_object_or_404(User, username=username)
        # user_profile = get_object_or_404(UserProfile, user=user)
        #user_info= user_profile.objects.values('id', 'name', 'role', 'email',
        #            'date_joined', 'bio', 'categories')

        #username = user.data.username

        print(f"Looking for user with username: {username}")  # Debug print
        user = User.objects.filter(username=username).first()
        if not user:
            print(f"No user found with username: {username}")  # Debug print
            return JsonResponse({
                "status": False,
                "message": f"User with username {username} not found."
            }, status=404)

        user_profile = UserProfile.objects.filter(user=user).first()
        if not user_profile:
            print(f"No profile found for user: {username}")  # Debug print
            return JsonResponse({
                "status": False,
                "message": f"Profile not found for user {username}"
            }, status=404)
        
        user_data = {
            'id': user.id,
            'username': username,
            'name': user_profile.name,
            'role': user_profile.role,
            'email': user_profile.email,
            'date_joined': user.date_joined,
            'bio': user_profile.bio,
            'categories': user_profile.categories
        }

        return JsonResponse({
            "status": True,
            "message": "User profile retrieved successfully.",
            #"data": list(user_info)  # Wrap in list to match the format
            "data": [user_data]
        }, status=200)
        
    except Exception as e:
        print(e)
        return JsonResponse({
            "status": False,
            "message": "User profile not found."
        }, status=404)


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
