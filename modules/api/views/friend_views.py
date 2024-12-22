from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
from modules.api.ApiResponse import ApiResponse
from eventyog.decorators import check_user_profile, check_user_profile_api
from modules.main.models import UserProfile, User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from eventyog.types import AuthRequest

@csrf_exempt
@check_user_profile_api()
def show_list(request):
    try:
        friends = request.user_profile.friends.all()
        for friend in friends:
            user = friend.user
            friend.user_id = user.id


        friends_recommendation = UserProfile.objects.all().exclude(user=request.user)

        temp = []
        
        if request.user_profile.categories is None:
            request.user_profile.categories = ''

        for friend in friends_recommendation:
            if friend not in friends and (set((friend.categories or '').split(',')) & set((request.user_profile.categories or '').split(',')) or friend.categories == ''):
                temp.append(friend)

        friends_recommendation = temp

        context = {
            'friends': [
            {
                'id': friend.user.id,
                'profile_picture': friend.profile_picture.url if friend.profile_picture else '',
                'username': friend.user.username,
                'email': friend.user.email,
                'categories': friend.categories.split(',') if friend.categories is not None else [],
                'is_friend': True
            } for friend in friends
            ],
            'friends_recommendation': [
            {
                'id': friend.user.id,
                'profile_picture': friend.profile_picture.url if friend.profile_picture else '',
                'username': friend.user.username,
                'email': friend.user.email,
                'categories':friend.categories.split(',') if friend.categories is not None else [],
                'is_friend': False
            } for friend in friends_recommendation
            ],
        }
        
        print('context')
        print(context)
        
        return JsonResponse({
            'status': True,
            'message': 'Sucessfully retrieve Friend list',
            'data': context
        })
    except Exception as e:
        print('error')
        print(str(e))
        return JsonResponse({
            'status': False,
            'message': 'Failed to retrieve Friend list',
            'error': str(e)
        })

# Show friend detail
@check_user_profile_api()
def main(request: HttpRequest, user_id: int) -> JsonResponse:
    try:
        friend = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'status': False,
            'message': 'User not found'
        })

    if friend.categories == '':
        categories = None
    else:
        categories = friend.categories.split(',')

    is_friend = request.user_profile.friends.all().filter(user=friend.user).exists()

    context = {
        'friend': {
            'id': friend.user.id,
            'username': friend.user.username,
            'email': friend.user.email,
            'categories': categories if categories else []
        },
        'is_friend': is_friend,
    }

    return JsonResponse({
        'status': True,
        'message': 'Successfully retrieve friend detail',
        'data': context
    })
    
@csrf_exempt
@check_user_profile_api()
def add_friend_ajax(request: HttpRequest, friend_id: str) -> JsonResponse:
    try:
        user = request.user
        user_profile = request.user_profile
        friend = get_object_or_404(User, id=friend_id)
        friend_profile = get_object_or_404(UserProfile, user=friend)

        if user == friend:
            return JsonResponse({'status': False, 'message': 'You cannot add yourself as a friend.'})

        if user_profile.friends.filter(id=friend.id).exists():
            return JsonResponse({'status': False, 'message': 'You are already friends with this user.'})

        user_profile.friends.add(friend_profile)
        friend_profile.friends.add(user_profile)

        return JsonResponse({'status': True, 'message': 'Friend added successfully.'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': 'Failed to add friend', 'error': str(e)})


@csrf_exempt
@check_user_profile(is_redirect=True)
def remove_friend(request: AuthRequest, friend_id: str) -> JsonResponse:
    try:
        user_profile = request.user_profile
        friend = get_object_or_404(User, id=friend_id)
        friend_profile = get_object_or_404(UserProfile, user=friend)

        if not user_profile.friends.filter(user=friend).exists():
            return JsonResponse({'status': False, 'message': 'You are not friends with this user.'})

        user_profile.friends.remove(friend_profile)
        friend_profile.friends.remove(user_profile)

        return JsonResponse({'status': True, 'message': 'Friend removed successfully.'})
    except Exception as e:
        return JsonResponse({'status': False, 'message': 'Failed to remove friend', 'error': str(e)})