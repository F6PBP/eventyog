from django.urls import path

from modules.api.views import auth_views
from .views.forum_views import *
app_name = 'api'


urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('yogforum/', main, name='main'),
    path('yogforum/post/<int:post_id>/', viewforum, name='viewforum'),
    path('yogforum/add-post/', add_post, name='add_post'),
    path('yogforum/post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('yogforum/reply/<int:reply_id>/delete/', delete_reply, name='delete_reply'),
    path('yogforum/post/<int:post_id>/add_reply/', add_reply, name='add_reply'),
    path('yogforum/reply/<int:reply_id>/', view_reply_as_post, name='view_reply_as_post'), 
    path('yogforum/edit/<int:post_id>/', edit_post, name='edit_post'),
    path('yogforum/like_post/<int:id>/', like_post, name='like_post'),
    path('yogforum/dislike_post/<int:id>/', dislike_post, name='dislike_post'),
    path('yogforum/like_reply/<int:id>/', like_reply, name='like_reply'),
    path('yogforum/dislike_reply/<int:id>/', dislike_reply, name='dislike_reply'),
]