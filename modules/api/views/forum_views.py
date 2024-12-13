import json
from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply
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
@login_required
def like_post(request, id):
    post = get_object_or_404(Forum, id=id)
    user_profile = request.user.userprofile

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

@csrf_exempt
@login_required
def dislike_post(request, id):
    post = get_object_or_404(Forum, id=id)
    user_profile = request.user.userprofile

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

@csrf_exempt
@login_required
def like_reply(request, id):
    reply = get_object_or_404(ForumReply, id=id)
    user_profile = request.user.userprofile

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

@csrf_exempt
@login_required
def dislike_reply(request, id):
    reply = get_object_or_404(ForumReply, id=id)
    user_profile = request.user.userprofile

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

@csrf_exempt
@login_required
def add_post(request):
    if request.method == 'POST':
        # Parse data dari request body (untuk mendukung JSON jika diperlukan)
        data = json.loads(request.body)

        # Validasi data menggunakan form
        form = AddForm(data)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.userprofile  # Mengambil profil pengguna dari user yang login
            post.save()
            return JsonResponse({
                'success': True,
                'message': 'Post added successfully!',
                'post_id': post.id  # Mengembalikan ID post yang baru
            }, status=201)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid form data.',
                'errors': form.errors  # Kirim error jika form tidak valid
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)


@csrf_exempt
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Forum, id=post_id, user=request.user.userprofile)
    post.delete()
    return JsonResponse({'success': True, 'message': 'Post deleted successfully!'})

@csrf_exempt
@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id, user=request.user.userprofile)
    reply.delete()
    return JsonResponse({'success': True, 'message': 'Reply deleted successfully!'})

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
@login_required
def add_reply(request, post_id):
    forum_post = get_object_or_404(Forum, id=post_id)
    reply_to_id = request.POST.get('reply_to')

    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'success': False, 'message': 'Content cannot be empty.'})

        reply_to = get_object_or_404(ForumReply, id=reply_to_id) if reply_to_id else None
        reply = ForumReply.objects.create(
            user=request.user.userprofile,
            forum=forum_post,
            content=content,
            reply_to=reply_to
        )
        return JsonResponse({'success': True, 'message': 'Reply added successfully!', 'reply_id': reply.id})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@csrf_exempt
@login_required
def edit_post(request, post_id):
    post_object = get_object_or_404(Forum, id=post_id, user=request.user.userprofile)

    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post_object)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Post edited successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid form data.'})

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

