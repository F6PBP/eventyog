from django.urls import path
from modules.yogforum.views import *

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),
    path('post/<int:post_id>/', viewforum, name='viewforum'),
    path('add-post/', add_post, name='add_post'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', delete_reply, name='delete_reply'),
    path('post/<int:post_id>/add_reply/', add_reply, name='add_reply'),
    path('reply/<int:reply_id>/', view_reply_as_post, name='view_reply_as_post'), 
    path('edit/<int:post_id>/', edit_post, name='edit_post'),
]
