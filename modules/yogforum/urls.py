from django.urls import path
from modules.yogforum.views import *

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),
    path('get_forum_by_ajax/', get_forum_by_ajax, name='get_forum_by_ajax'),
    path('post/<int:post_id>/', viewforum, name='viewforum'),
    path('add-post/', add_post, name='add_post'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', delete_reply, name='delete_reply'),
    path('post/<int:post_id>/add_reply/', add_reply, name='add_reply'),
    path('reply/<int:reply_id>/', view_reply_as_post, name='view_reply_as_post'), 
    path('edit/<int:post_id>/', edit_post, name='edit_post'),
    path('like_post/<int:id>/', like_post, name='like_post'),
    path('dislike_post/<int:id>/', dislike_post, name='dislike_post'),
    path('like_reply/<int:id>/', like_reply, name='like_reply'),
    path('dislike_reply/<int:id>/', dislike_reply, name='dislike_reply'),
    path('forum/<int:forum_id>/json/', forum_detail_json, name='forum_detail_json'),
    path('reply/<int:reply_id>/json/', forum_reply_detail_json, name='forum_reply_detail_json'),
]
