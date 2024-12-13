from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from eventyog.types import AuthRequest
from eventyog.decorators import check_user_profile
from modules.main.models import UserProfile, User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from modules.main.models import UserProfile, User

@check_user_profile()
def show_list(request):
    friends = request.user_profile.friends.all()
    for friend in friends:
        user = friend.user
        friend.user_id = user.id
        
    # Get All User that has similar category with the current user
    friends_recommendation = UserProfile.objects.all().exclude(user=request.user)
    
    temp = []

    if request.user_profile.categories is None:
        request.user_profile.categories = ''
        
    for friend in friends_recommendation:
        if friend not in friends and (friend.categories.split(',') in request.user_profile.categories.split(',') or friend.categories == ''):
            temp.append(friend)
            
    friends_recommendation = temp

    context = {
        'friends': friends,
        'friends_recommendation': friends_recommendation,
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin
    }
    
    return render(request, 'friend_list.html', context)

@check_user_profile()
def main(request: AuthRequest, user_id: int):
    try:
        friend = get_object_or_404(User, id=user_id)
        friend_profile = get_object_or_404(UserProfile, user=friend)
    except:
        return redirect('main:main')
    
    if (friend == request.user):
        return redirect('auth:profile')

    if (friend_profile.categories == ''):
        categories = None
    else:
        categories = friend_profile.categories.split(',')
        
    is_friend = request.user_profile.friends.all().filter(user=friend).exists()
    
    context = {
        'user_id': user_id,
        'friend': friend,
        'friend_profile': friend_profile,
        'user': request.user,
        'user_profile': request.user_profile,
        'categories': categories,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
        'is_friend': is_friend
    }
    
    return render(request, 'friends.html', context)

@csrf_exempt
@require_POST
@check_user_profile(is_redirect=True)
def add_friend_ajax(request: AuthRequest, friend_id: int):
    user = request.user
    user_profile = request.user_profile
    friend = get_object_or_404(User, id=friend_id)
    friend_profile = get_object_or_404(UserProfile, user=friend)
    
    if (user == friend):
        return JsonResponse({'error': 'You cannot add yourself as a friend.'})
    
    if (user_profile.friends.filter(id=friend.id).exists()):
        return JsonResponse({'error': 'You are already friends with this user.'})
    
    user_profile.friends.add(friend_profile)
    friend_profile.friends.add(user_profile)
    
    return JsonResponse({'success': 'Friend added successfully.'})

@csrf_exempt
@require_POST
@check_user_profile(is_redirect=True)
def remove_friend(request: AuthRequest, friend_id: int):
    user_profile = request.user_profile
    friend = get_object_or_404(User, id=friend_id)
    friend_profile = get_object_or_404(UserProfile, user=friend)
    
    if (not user_profile.friends.filter(user=friend).exists()):
        print(user_profile.friends.all())
        return JsonResponse({'error': 'You are not friends with this user.'})

    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    
    return redirect('main:main')