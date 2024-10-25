from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.yogforum.forms import AddForm, AddReplyForm, EditPostForm

def viewforum(request, post_id):
    # Cari post berdasarkan post_id
    forum_post = get_object_or_404(Forum, id=post_id)
    
    # Ambil semua reply yang terkait dengan post ini
    replies = ForumReply.objects.filter(forum=forum_post, reply_to=None).order_by('created_at')

    context = {
        'forum_post': forum_post,
        'replies': replies,
        'show_navbar': True,
        'show_footer': True
    }
    return render(request, 'viewforum.html', context)

def main(request):
    # Ambil semua post
    forum_posts = Forum.objects.all().order_by('-created_at')
    
    context = {
        'forum_posts': forum_posts,
        'show_navbar': True,
        'show_footer': True
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
        # Try to get the forum post
        forum_post = Forum.objects.get(id=post_id)
        forum_reply = None
    except Forum.DoesNotExist:
        # If the forum post doesn't exist, it might be a reply
        forum_reply = get_object_or_404(ForumReply, id=post_id)
        forum_post = forum_reply.forum  # Get the original forum post from the reply

    # Get 'reply_to' ID (optional), which could be a reply or a post
    reply_to_id = request.POST.get('reply_to', None)

    if request.method == 'POST':
        content = request.POST.get('content')

        if reply_to_id:
            # The reply is in response to another reply
            reply_to = get_object_or_404(ForumReply, id=reply_to_id)
            ForumReply.objects.create(
                user=request.user.userprofile,
                forum=forum_post,
                content=content,
                reply_to=reply_to
            )
        else:
            # The reply is to the original forum post or the reply acting as a post
            ForumReply.objects.create(
                user=request.user.userprofile,
                forum=forum_post,
                content=content,
                reply_to=forum_reply  # This will be None if it's replying to the post
            )

        # Redirect to the view forum page or reply as post page depending on the context
        if forum_reply:
            return redirect('yogforum:view_reply_as_post', reply_id=forum_reply.id)
        else:
            return redirect('yogforum:viewforum', post_id=forum_post.id)

    return redirect('yogforum:viewforum', post_id=forum_post.id)

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
    try:
        # Try to get the forum post first
        post_object = get_object_or_404(Forum, id=post_id, user=request.user.userprofile)
    except Forum.DoesNotExist:
        # If the forum post does not exist, try finding a reply instead
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