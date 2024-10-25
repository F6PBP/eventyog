from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from modules.yogforum.forms import ForumForm

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

@login_required
def add_post(request):
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user.userprofile  # Asosiasikan post dengan user yang sedang login
            new_post.save()
            messages.success(request, 'Your post has been successfully added!')
            return redirect('yogforum:main')
    return redirect('yogforum:main')