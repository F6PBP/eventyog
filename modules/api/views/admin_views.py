from  django.http import HttpRequest, JsonResponse
from modules.api.ApiResponse import ApiResponse
import json

def main(request: HttpRequest) -> ApiResponse:
    return ApiResponse(status=200, content="Hello, World!")

from django.views.decorators.csrf import csrf_exempt
from eventyog.decorators import check_user_profile, check_user_profile_api

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

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=False)
def show_main(request: AuthRequest) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)

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

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def see_user(request, username) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)
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
@csrf_exempt        
def edit_user(request, username) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({"status": False, "message": "Access denied."}, status=403)
     
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

    if request.method == 'POST':
        print(request.POST)
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user  # Associate profile with logged-in user
            profile.save()

            return JsonResponse({
                "status": True,
                "message": "Profile updated successfully."
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Form is not valid.",
                "errors": form.errors
            }, status=400)
    else:
        form = UserProfileForm(instance=user_profile)
        context = {
            'user': user,
            'user_profile': user_profile,
            'image_url': user.image_url,
            'categories': user_profile.categories,
            'form': form,
            'show_navbar': True,
            'show_footer': True
        }

        return JsonResponse({
            "status": True,
            "message": "Profile edit form retrieved successfully.",
            "data": context
        }, status=200)

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def delete_user(request, username) -> JsonResponse:
    if request.user_profile.role != 'AD':
        return JsonResponse({
            "status": False,
            "message": "You do not have permission to perform this action."
        }, status=403)  

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
    
    try:
       #if request.method == 'POST':
        user_profile.delete()
        user.delete()
        return JsonResponse({
            "status": True,
            "message": "Profile deleted successfully.",
            "status_code": 200
        }, status=200)
    
    except Exception as e:
        print(e)
        user.delete()
        return JsonResponse({
            "status": False,
            "message": "Error occurred while deleting profile.",
            "status_code": 500
        }, status=500)

# @login_required(login_url='auth:login')
# @check_user_profile(is_redirect=True)
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
