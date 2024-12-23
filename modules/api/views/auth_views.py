from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
from modules.main.models import UserProfile
from modules.authentication.forms import UserProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from eventyog.decorators import check_user_profile, check_user_profile_api

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    
    print(username, password)
    
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            # Status login sukses.
            try:
                user_profile = UserProfile.objects.get(user=user)
                request.is_admin = user_profile.role == 'AD'
                request.image_url = (
                    f'https://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
                    if user_profile.profile_picture
                    else 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
                )
            except:
                request.is_admin = False
                request.image_url = 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
            
            return JsonResponse({
                "username": user.username,
                "isAdmin": request.is_admin,
                "imageUrl": request.image_url,
                "status": True,
                "message": "Login sukses!"
                # Tambahkan data lainnya jika ingin mengirim data ke Flutter.
            }, status=200)
        else:
            print('Login gagal, akun dinonaktifkan.')
            return JsonResponse({
                "status": False,
                "message": "Login gagal, akun dinonaktifkan."
            }, status=401)

    else:
        print('Login gagal, periksa kembali email atau kata sandi.')
        return JsonResponse({
            "status": False,
            "message": "Login gagal, periksa kembali email atau kata sandi."
        }, status=401)
        
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

        # Check if the passwords match
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # Create the new user
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
def logout(request):
    username = request.user.username

    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logout berhasil!"
        }, status=200)
    except:
        return JsonResponse({
        "status": False,
        "message": "Logout gagal."
        }, status=401)
            
@csrf_exempt
def onboarding(request):
    profile = UserProfile.objects.filter(user=request.user)
    if profile.exists():
        return JsonResponse({
            "status": True,
            "message": "User has profile.",
            "profile": list(profile.values())
        }, status=200)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return JsonResponse({
                "status": True,
                "message": "Profile created successfully!"
            }, status=200)
        else:
            print(request.FILES)
            return JsonResponse({
                "status": False,
                "message": "Form is not valid.",
                "errors": form.errors
            }, status=400)
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)
        
@csrf_exempt   
@check_user_profile_api()     
def profile(request):
    if request.method == "GET":
        print(request.user)
        try:
            if request.user_profile.categories == '' or request.user_profile.categories == None:
                categories = ''
            else:
                categories = request.user_profile.categories

            context = {
                'username': request.user.username,
                'name': request.user_profile.name,
                'wallet': request.user_profile.wallet,
                'email': request.user_profile.email,
                'date_joined': request.user.date_joined,
                'bio': request.user_profile.bio,
                'image_url': request.image_url,
                'categories': categories,
                'is_admin': request.is_admin,
            }

            return JsonResponse({
                "status": True,
                "message": "Profile retrieved successfully.",
                "data": context
            }, status=200)

        except Exception as e:
            print(e)
            print('User profile not found.')
            return JsonResponse({
                "status": False,
                "message": "User profile not found."
            }, status=404)

@csrf_exempt        
@check_user_profile_api()
def edit_profile(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserProfileForm(request.POST, request.FILES, instance=request.user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate profile with logged-in user
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
        form = UserProfileForm(instance=request.user_profile)
        context = {
            'user': request.user,
            'user_profile': request.user_profile,
            'image_url': request.image_url,
            'categories': request.user_profile.categories,
            'form': form,
            'show_navbar': True,
            'show_footer': True
        }

        return JsonResponse({
            "status": True,
            "message": "Profile edit form retrieved successfully.",
            "data": context
        }, status=200)

@csrf_exempt
def delete_profile(request):
    try:
        if request.method == 'POST':
            request.user_profile.delete()
            request.user.delete()
            logout(request)
            return JsonResponse({
                "status": True,
                "message": "Profile deleted successfully."
            }, status=200)
    except Exception as e:
        print(e)
        request.user.delete()
        logout(request)
        return JsonResponse({
            "status": False,
            "message": "Error occurred while deleting profile."
        }, status=500)

    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)