from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def show_forum(request):
    images = [
        {'url': r'https://cdn-assetd.kompas.id/7MxyRTqX2bZAZI7a9rb998LXCl4=/1024x683/https%3A%2F%2Fasset.kgnewsroom.com%2Fphoto%2Fpre%2F2023%2F10%2F07%2Fc1666929-678a-4e6c-96e1-623c34a80b48_jpg.jpg'},
        {'url': r'https://cdn-assetd.kompas.id/7MxyRTqX2bZAZI7a9rb998LXCl4=/1024x683/https%3A%2F%2Fasset.kgnewsroom.com%2Fphoto%2Fpre%2F2023%2F10%2F07%2Fc1666929-678a-4e6c-96e1-623c34a80b48_jpg.jpg'},
        {'url': r'https://cdn-assetd.kompas.id/7MxyRTqX2bZAZI7a9rb998LXCl4=/1024x683/https%3A%2F%2Fasset.kgnewsroom.com%2Fphoto%2Fpre%2F2023%2F10%2F07%2Fc1666929-678a-4e6c-96e1-623c34a80b48_jpg.jpg'},
        {'url': r'https://cdn-assetd.kompas.id/7MxyRTqX2bZAZI7a9rb998LXCl4=/1024x683/https%3A%2F%2Fasset.kgnewsroom.com%2Fphoto%2Fpre%2F2023%2F10%2F07%2Fc1666929-678a-4e6c-96e1-623c34a80b48_jpg.jpg'},
        {'url': r'https://cdn-assetd.kompas.id/7MxyRTqX2bZAZI7a9rb998LXCl4=/1024x683/https%3A%2F%2Fasset.kgnewsroom.com%2Fphoto%2Fpre%2F2023%2F10%2F07%2Fc1666929-678a-4e6c-96e1-623c34a80b48_jpg.jpg'}
    ]
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'images': images
    }
    
    return render(request, 'forum.html', context)