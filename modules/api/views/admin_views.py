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

#@login_required(login_url='auth:login')
#@check_user_profile(is_redirect=False)
def show_main(request: AuthRequest) -> JsonResponse:
    
    # Get All User and its userProfile
    user = User.objects.all()
    
    # Serialize the data
    user_data = []    
    
    for u in user:
        try:
            user_profile = UserProfile.objects.get(user=u)
            user_data.append({
                'id': u.id,
                'username': u.username,
                'name': user_profile.name,
                'email': user_profile.email,
                'role': user_profile.role,
                'date_joined': u.date_joined,
                'bio': user_profile.bio,
                'categories': user_profile.categories,
                'profile_picture': (
                    f'https://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
                    if user_profile.profile_picture
                    else 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
                )
            })
        except UserProfile.DoesNotExist:
            continue
        
    print(user_data)
    
    return JsonResponse({
        "status": True,
        "message": "Admin data retrieved successfully.",
        "data": user_data
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

# @login_required(login_url='auth:login')
# @check_user_profile(is_redirect=True)
def see_user(request, username) -> JsonResponse:
    # if request.user_profile.role != 'AD':
    #     return JsonResponse({"status": False, "message": "Access denied."}, status=403)
    try:
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


# @login_required(login_url='auth:login')
# @check_user_profile(is_redirect=True)
@csrf_exempt        
def edit_user(request, username) -> JsonResponse:
    # if request.user_profile.role != 'AD':
    #     return JsonResponse({"status": False, "message": "Access denied."}, status=403)
     
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

# @login_required(login_url='auth:login')
# @check_user_profile(is_redirect=True)
def delete_user(request, username) -> JsonResponse:
    # if request.user_profile.role != 'AD':
    #     return JsonResponse({
    #         "status": False,
    #         "message": "You do not have permission to perform this action."
    #     }, status=403)  

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

# # @login_required(login_url='auth:login')
# # @check_user_profile(is_redirect=True)
@csrf_exempt
def create_user(request) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        data = json.loads(request.body)
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')

        # Validate required fields
        if not all([username, email, password1, password2]):
            return JsonResponse({
                "status": False,
                "message": "All fields are required."
            }, status=400)

        # Check if passwords match
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)

        # Validate password length
        if len(password1) < 8:
            return JsonResponse({
                "status": False,
                "message": "Password must be at least 8 characters long."
            }, status=400)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "status": False,
                "message": "Email already exists."
            }, status=400)

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()
        
        # Create a basic user profile with only provided fields
        UserProfile.objects.create(
            user=user,
            name=name or '',  # Default to None if not provided
            email=email,  # From the user creation
            bio='',  # Optional, defaults to None
            categories=None,  # Optional, defaults to None
            profile_picture=''  # Optional, defaults to None
        )

        return JsonResponse({
            "status": True,
            "message": "User and profile created successfully!",
            "username": user.username,
            "email": user.email,
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": False,
            "message": "Invalid JSON format."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Error creating user: {str(e)}"
        }, status=500)
