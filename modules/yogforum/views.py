from django.shortcuts import render, redirect, get_object_or_404
from modules.main.models import Forum, ForumReply
from django.http import JsonResponse
from django.http import HttpRequest, HttpResponse

def viewforum(request, post_id):
    # Cari post berdasarkan post_id
    forum_post = get_object_or_404(Forum, id=post_id)
    
    # Ambil semua reply yang terkait dengan post ini
    replies = ForumReply.objects.filter(forum=forum_post).order_by('created_at')

    context = {
        'forum_post': forum_post,
        'replies': replies,
    }
    return render(request, 'viewforum.html', context)

def main(request):
    # Ambil semua post
    forum_posts = Forum.objects.all().order_by('-created_at')
    
    context = {
        'forum_posts': forum_posts
    }
    return render(request, 'yogforum.html', context)