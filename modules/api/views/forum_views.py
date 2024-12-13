import json
from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply, UserProfile
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.yogforum.forms import AddForm, AddReplyForm, EditPostForm

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.main.models import Forum, ForumReply
from modules.yogforum.forms import AddForm, AddReplyForm, EditPostForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


def main(request):
    forum_posts = Forum.objects.all().order_by('-created_at')
    
    posts_data = []
    for post in forum_posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'user': post.user.user.username,
            'content': post.content,
            'created_at': post.created_at,
            'total_likes': post.totalLike(),
            'total_dislikes': post.totalDislike(),
        })
    
    return JsonResponse({
        'forum_posts': posts_data,
        'show_navbar': True,
        'show_footer': True
    })

@csrf_exempt
def viewforum(request, post_id):
    forum_post = get_object_or_404(Forum, id=post_id)

    def get_nested_replies(reply):
        """Recursive function to fetch nested replies."""
        nested_replies = ForumReply.objects.filter(reply_to=reply).order_by('created_at')
        return [
            {
                'id': nested_reply.id,
                'content': nested_reply.content,
                'user': nested_reply.user.user.username,
                'total_likes': nested_reply.totalLike(),
                'total_dislikes': nested_reply.totalDislike(),
                'created_at': nested_reply.created_at,
                'replies': get_nested_replies(nested_reply),  # Recursive call
            }
            for nested_reply in nested_replies
        ]

    replies = ForumReply.objects.filter(forum=forum_post, reply_to=None).order_by('created_at')
    reply_data = [
        {
            'id': reply.id,
            'content': reply.content,
            'user': reply.user.user.username,
            'total_likes': reply.totalLike(),
            'total_dislikes': reply.totalDislike(),
            'created_at': reply.created_at,
            'replies': get_nested_replies(reply),  # Nested replies
        }
        for reply in replies
    ]

    return JsonResponse({
        'success': True,
        'forum_post': {
            'id': forum_post.id,
            'title': forum_post.title,
            'content': forum_post.content,
            'user': forum_post.user.user.username,
            'total_likes': forum_post.totalLike(),
            'total_dislikes': forum_post.totalDislike(),
            'created_at': forum_post.created_at,
        },
        'replies': reply_data,
    })

@csrf_exempt
def view_reply_as_post(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id)

    def get_nested_replies(reply):
        """Recursive function to fetch nested replies."""
        nested_replies = ForumReply.objects.filter(reply_to=reply).order_by('created_at')
        return [
            {
                'id': nested_reply.id,
                'content': nested_reply.content,
                'user': nested_reply.user.user.username,
                'total_likes': nested_reply.totalLike(),
                'total_dislikes': nested_reply.totalDislike(),
                'created_at': nested_reply.created_at,
                'replies': get_nested_replies(nested_reply),  
            }
            for nested_reply in nested_replies
        ]

    return JsonResponse({
        'success': True,
        'reply': {
            'id': reply.id,
            'content': reply.content,
            'user': reply.user.user.username,
            'forum_id': reply.forum.id,
            'reply_to': reply.reply_to.id if reply.reply_to else None,
            'total_likes': reply.totalLike(),
            'total_dislikes': reply.totalDislike(),
            'created_at': reply.created_at,
            'replies': get_nested_replies(reply),  
        },
    })

@csrf_exempt
def add_post(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        username = data.get('username')  # Ambil username dari JSON request
        if not username:
            return JsonResponse({
                'success': False,
                'message': 'Username is required.'
            }, status=400)

        user, created = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        # Validasi form dan simpan post
        form = AddForm(data)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user_profile
            post.save()

            return JsonResponse({
                'success': True,
                'message': 'Post added successfully!',
                'post_id': post.id
            }, status=201)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid form data.',
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def like_post(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        post = get_object_or_404(Forum, id=id)

        if user_profile in post.like.all():
            post.like.remove(user_profile)
            liked = False
        else:
            post.like.add(user_profile)
            liked = True
            if user_profile in post.dislike.all():
                post.dislike.remove(user_profile)

        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': post.totalLike(),
            'total_dislikes': post.totalDislike(),
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def dislike_post(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)
        
        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        post = get_object_or_404(Forum, id=id)

        if user_profile in post.dislike.all():
            post.dislike.remove(user_profile)
            disliked = False
        else:
            post.dislike.add(user_profile)
            disliked = True
            if user_profile in post.like.all():
                post.like.remove(user_profile)

        return JsonResponse({
            'success': True,
            'disliked': disliked,
            'total_likes': post.totalLike(),
            'total_dislikes': post.totalDislike(),
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def like_reply(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        reply = get_object_or_404(ForumReply, id=id)

        if user_profile in reply.like.all():
            reply.like.remove(user_profile)
            liked = False
        else:
            reply.like.add(user_profile)
            liked = True
            if user_profile in reply.dislike.all():
                reply.dislike.remove(user_profile)

        return JsonResponse({
            'success': True,
            'liked': liked,
            'total_likes': reply.totalLike(),
            'total_dislikes': reply.totalDislike(),
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def dislike_reply(request, id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        reply = get_object_or_404(ForumReply, id=id)

        if user_profile in reply.dislike.all():
            reply.dislike.remove(user_profile)
            disliked = False
        else:
            reply.dislike.add(user_profile)
            disliked = True
            if user_profile in reply.like.all():
                reply.like.remove(user_profile)

        return JsonResponse({
            'success': True,
            'disliked': disliked,
            'total_likes': reply.totalLike(),
            'total_dislikes': reply.totalDislike(),
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def delete_post(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        post = get_object_or_404(Forum, id=post_id, user=user_profile)
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post deleted successfully!'})

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def delete_reply(request, reply_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        reply = get_object_or_404(ForumReply, id=reply_id, user=user_profile)
        reply.delete()
        return JsonResponse({'success': True, 'message': 'Reply deleted successfully!'})

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@csrf_exempt
def add_reply(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        forum_post = get_object_or_404(Forum, id=post_id)
        reply_to_id = data.get('reply_to')
        content = data.get('content')

        if not content:
            return JsonResponse({'success': False, 'message': 'Content cannot be empty.'}, status=400)

        reply_to = get_object_or_404(ForumReply, id=reply_to_id) if reply_to_id else None
        reply = ForumReply.objects.create(
            user=user_profile,
            forum=forum_post,
            content=content,
            reply_to=reply_to
        )
        return JsonResponse({'success': True, 'message': 'Reply added successfully!', 'reply_id': reply.id})

    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    }, status=405)

@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        data = request.POST if request.content_type == 'application/x-www-form-urlencoded' else json.loads(request.body)
        
        # Jika data diambil dari JSON, pastikan username juga diambil
        username = data.get('username')
        if not username:
            return JsonResponse({'success': False, 'message': 'Username is required.'}, status=400)

        user, _ = User.objects.get_or_create(username=username)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        # Pastikan untuk mengambil post dengan user_profile
        post_object = get_object_or_404(Forum, id=post_id, user=user_profile)
        
        # Jika data dari JSON, ubah jadi QueryDict untuk form
        if not isinstance(data, dict):
            # Jika masih bukan dict, berarti data = request.POST diatas
            pass
        else:
            # Convert JSON data ke QueryDict untuk form 
            from django.http import QueryDict
            qd = QueryDict('', mutable=True)
            for key, value in data.items():
                qd[key] = value
            data = qd

        form = EditPostForm(data, instance=post_object)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Post edited successfully!'})

        return JsonResponse({'success': False, 'message': 'Invalid form data.', 'errors': form.errors}, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)



