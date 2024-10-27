from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from modules.main.models import Forum, ForumReply
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.yogforum.forms import AddForm, AddReplyForm, EditPostForm

@login_required
def like_post(request, id):
    post = get_object_or_404(Forum, id=id)
    user_profile = request.user.userprofile

    liked = False
    disliked = False

    if user_profile in post.like.all():
        post.like.remove(user_profile)
        liked = False
    else:
        post.like.add(user_profile)
        liked = True
        if user_profile in post.dislike.all():
            post.dislike.remove(user_profile)
            disliked = True

    return JsonResponse({
        'success': True,
        'total_likes': post.totalLike(),
        'liked': liked,
        'disliked': disliked,
        'total_dislikes': post.totalDislike() 
    })

@login_required
def dislike_post(request, id):
    post = get_object_or_404(Forum, id=id)
    user_profile = request.user.userprofile

    liked = False
    disliked = False

    if user_profile in post.dislike.all():
        post.dislike.remove(user_profile)
        disliked = False
    else:
        post.dislike.add(user_profile)
        disliked = True
        if user_profile in post.like.all():
            post.like.remove(user_profile)
            liked = True

    return JsonResponse({
        'success': True,
        'total_dislikes': post.totalDislike(),
        'disliked': disliked,
        'liked': liked,
        'total_likes': post.totalLike() 
    })

@login_required
def like_reply(request, id):
    reply = get_object_or_404(ForumReply, id=id)
    user_profile = request.user.userprofile  

    liked = False
    disliked = False

    if user_profile in reply.like.all():
        reply.like.remove(user_profile) 
        liked = False
    else:
        reply.like.add(user_profile)  
        liked = True
        
        if user_profile in reply.dislike.all():
            reply.dislike.remove(user_profile)
            disliked = True

    return JsonResponse({
        'success': True,
        'total_likes': reply.totalLike(),
        'total_dislikes': reply.totalDislike(),
        'liked': liked,
        'disliked': disliked,
    })

@login_required
def dislike_reply(request, id):
    reply = get_object_or_404(ForumReply, id=id)
    user_profile = request.user.userprofile

    liked = False
    disliked = False

    if user_profile in reply.dislike.all():
        reply.dislike.remove(user_profile) 
        disliked = False
    else:
        reply.dislike.add(user_profile)  
        disliked = True
        
        if user_profile in reply.like.all():
            reply.like.remove(user_profile)
            liked = True

    return JsonResponse({
        'success': True,
        'total_dislikes': reply.totalDislike(),
        'total_likes': reply.totalLike(),
        'disliked': disliked,
        'liked': liked,
    })

from eventyog.decorators import check_user_profile
from modules.main.models import UserProfile
from django.utils.timesince import timesince

def viewforum(request, post_id):
    forum_post = get_object_or_404(Forum, id=post_id)
    
    # Ambil semua reply yang terkait dengan post ini
    replies = ForumReply.objects.filter(forum=forum_post, reply_to=None).order_by('created_at')

    context = {
        'forum_post': forum_post,
        'replies': replies,
        'show_navbar': True,
        'show_footer': True,
    }
    return render(request, 'viewforum.html', context)

def get_forum_by_ajax(request):
    search = request.GET.get('search')
    
    forum_posts = Forum.objects.all().order_by('-created_at')
    
    if search:
        forum_posts = Forum.objects.filter(title__icontains=search).order_by('-created_at')
    
        
    for post in forum_posts:
        post.user.profile_picture = 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
        if post.user.profile_picture:
            post.user.profile_picture = f'{post.user.profile_picture}'
    
    temp = []
    
    for post in forum_posts:
        replies_count = ForumReply.objects.filter(forum=post, reply_to=None).order_by('created_at').count()
        user = UserProfile.objects.get(id=post.user.id)

        print(user.user.username)   
        
        temp.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'user': user.user.username,
            'created_at': timesince(post.created_at),
            'profile_picture': post.user.profile_picture,
            'totalLike': post.totalLike(),    
            'totalDislike': post.totalDislike(),
            'comment_count': replies_count
        })
    
    return JsonResponse({
        'forum_posts': temp
    })

@check_user_profile()
def main(request):
    # Ambil semua post
    forum_posts = Forum.objects.all().order_by('-created_at')
    
    for post in forum_posts:
        if post.user.profile_picture:
            post.user.profile_picture = f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{post.user.profile_picture}.jpg'
        else:
            post.user.profile_picture = 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
    
    top_creators = Forum.objects.values('user').annotate(total=Count('user')).order_by('-total')[:10]
    
    for creator in top_creators:
        user = UserProfile.objects.get(id=creator['user'])
        creator['username'] = user.user.username
        if user.profile_picture:
            creator['profile_picture'] = f'http://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user.profile_picture}.jpg'
        else:
            creator['profile_picture'] = 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
    
    context = {
        'forum_posts': forum_posts,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
        'top_creators': top_creators
    }
    return render(request, 'yogforum.html', context)

def add_post(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.userprofile  # assuming user has a related profile
            post.save()
            return redirect('yogforum:main')  # redirect to forum main page after adding post
    else:
        form = AddForm()
    
    return render(request, 'components/new_post_modal.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Forum, id=post_id, user=request.user.userprofile)
    post.delete()
    return redirect('yogforum:main')

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id, user=request.user.userprofile)
    reply.delete()
    return redirect('yogforum:viewforum', post_id=reply.forum.id)

def viewforum(request, post_id):
    # Cari post berdasarkan post_id
    forum_post = get_object_or_404(Forum, id=post_id)
    
    # Ambil semua reply yang terkait dengan post ini
    replies = ForumReply.objects.filter(forum=forum_post, reply_to=None).order_by('created_at')

    # Check if user is replying to a specific reply
    reply_id = request.GET.get('reply_to', None)
    reply = None
    if reply_id:
        reply = get_object_or_404(ForumReply, id=reply_id)

    context = {
        'forum_post': forum_post,
        'replies': replies,
        'reply': reply,  # Send the specific reply to the template if replying to a reply
        'show_navbar': True,
        'show_footer': True
    }
    return render(request, 'viewforum.html', context)

@login_required
def add_reply(request, post_id):
    try:
        forum_post = Forum.objects.get(id=post_id)
        forum_reply = None
    except Forum.DoesNotExist:
        forum_reply = get_object_or_404(ForumReply, id=post_id)
        forum_post = forum_reply.forum

    reply_to_id = request.POST.get('reply_to', None)

    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            messages.error(request, "Content cannot be empty.")
            return redirect('yogforum:viewforum', post_id=forum_post.id)

        if reply_to_id:
            reply_to = get_object_or_404(ForumReply, id=reply_to_id)
            
            # Check reply depth before creating a new reply
            if get_reply_depth(reply_to) >= 2:
                messages.warning(request, "This post has reached the maximum number of replies.")
                return redirect('yogforum:view_reply_as_post', reply_id=forum_reply.id if forum_reply else forum_post.id)
            
            # Create the reply if depth is within the allowed limit
            ForumReply.objects.create(
                user=request.user.userprofile,
                forum=forum_post,
                content=content,
                reply_to=reply_to
            )
            messages.success(request, "Reply added successfully!")
        else:
            ForumReply.objects.create(
                user=request.user.userprofile,
                forum=forum_post,
                content=content,
                reply_to=forum_reply
            )
            messages.success(request, "Reply added successfully!")

        if forum_reply:
            return redirect('yogforum:view_reply_as_post', reply_id=forum_reply.id)
        else:
            return redirect('yogforum:viewforum', post_id=forum_post.id)

    return redirect('yogforum:viewforum', post_id=forum_post.id)

def get_reply_depth(reply):
    depth = 0
    while reply.reply_to is not None:
        reply = reply.reply_to
        depth += 1
    return depth

def view_reply_as_post(request, reply_id):
    # Get the reply by id
    reply_as_post = get_object_or_404(ForumReply, id=reply_id)
    
    # Get replies to this "reply" (nested replies)
    replies = ForumReply.objects.filter(reply_to=reply_as_post)
    
    context = {
        'forum_post': reply_as_post,  # treat reply as post
        'replies': replies,           # replies to the reply
        'show_navbar': True,
        'show_footer': True
    }
    
    return render(request, 'components/view_reply_as_post.html', context)

@login_required
def edit_post(request, post_id):
    post_object = None
    
    # Try to get the Forum post first
    try:
        post_object = Forum.objects.get(id=post_id, user=request.user.userprofile)
    except Forum.DoesNotExist:
        # If not found, try finding a reply instead
        post_object = get_object_or_404(ForumReply, id=post_id, user=request.user.userprofile)

    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post_object)
        if form.is_valid():
            form.save()
            if isinstance(post_object, Forum):
                return redirect('yogforum:viewforum', post_id=post_object.id)
            else:
                return redirect('yogforum:view_reply_as_post', reply_id=post_object.id)
    else:
        form = EditPostForm(instance=post_object)
    
    return render(request, 'components/edit_modal.html', {
        'form': form,
        'object': post_object,
        'modal_id': f"edit-modal-{post_id}"
    })

def forum_detail_json(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    data = {
        'id': forum.id,
        'title': forum.title,
        'content': forum.content,
        'created_at': forum.created_at,
        'updated_at': forum.updated_at,
        'user': forum.user.user.username,
        'total_likes': forum.totalLike(),
        'total_dislikes': forum.totalDislike(),
    }
    return JsonResponse(data)

def forum_reply_detail_json(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id)
    data = {
        'id': reply.id,
        'content': reply.content,
        'created_at': reply.created_at,
        'updated_at': reply.updated_at,
        'user': reply.user.user.username,
        'forum_id': reply.forum.id,
        'reply_to': reply.reply_to.id if reply.reply_to else None,
        'total_likes': reply.totalLike(),
        'total_dislikes': reply.totalDislike(),
    }
    return JsonResponse(data)