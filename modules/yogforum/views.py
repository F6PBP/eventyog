from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.yogforum.forms import AddForm, AddReplyForm

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

def view_forum(request, post_id):
    forum_post = get_object_or_404(Forum, id=post_id)
    replies = ForumReply.objects.filter(forum=forum_post)
    
    # Create a form instance for the reply
    if request.method == "POST":
        form = AddReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.forum = forum_post
            reply.user = request.user
            reply.save()
            # Redirect after saving
    else:
        form = AddReplyForm()

    context = {
        'forum_post': forum_post,
        'replies': replies,
        'form': form
    }
    return render(request, 'viewforum.html', context)

@login_required
def add_reply(request, post_id):
    forum_post = get_object_or_404(Forum, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_reply_id = request.POST.get('reply_to')

        # Creating a new reply
        new_reply = ForumReply(user=request.user.userprofile, forum=forum_post, content=content)

        if parent_reply_id:
            parent_reply = ForumReply.objects.get(id=parent_reply_id)
            new_reply.reply_to = parent_reply

        new_reply.save()
        return redirect('yogforum:viewforum', post_id=post_id)
    
    return redirect('yogforum:viewforum', post_id=post_id)