from django.urls import path
from modules.yogforum.views import *

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),
    path('post/<int:post_id>/', viewforum, name='viewforum'),
    path('add/', add_post, name='add_post'),  # Route untuk menambahkan post
]