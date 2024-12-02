from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('yogforum/get_forum_by_ajax/', forum_views.get_forum_by_ajax, name='forum_get_forum_by_ajax'),
    path('yogforum/post/<int:post_id>/', forum_views.viewforum, name='forum_viewforum'),
    path('yogforum/add-post/', forum_views.add_post, name='forum_add_post'),
    path('yogforum/post/<int:post_id>/delete/', forum_views.delete_post, name='forum_delete_post'),
    path('yogforum/reply/<int:reply_id>/delete/', forum_views.delete_reply, name='forum_delete_reply'),
    path('yogforum/post/<int:post_id>/add_reply/', forum_views.add_reply, name='forum_add_reply'),
    path('yogforum/reply/<int:reply_id>/', forum_views.view_reply_as_post, name='forum_view_reply_as_post'), 
    path('yogforum/edit/<int:post_id>/', forum_views.edit_post, name='forum_edit_post'),
    path('yogforum/like_post/<int:id>/', forum_views.like_post, name='forum_like_post'),
    path('yogforum/dislike_post/<int:id>/', forum_views.dislike_post, name='forum_dislike_post'),
    path('yogforum/like_reply/<int:id>/', forum_views.like_reply, name='forum_like_reply'),
    path('yogforum/dislike_reply/<int:id>/', forum_views.dislike_reply, name='forum_dislike_reply'),
    path('yogforum/forum/<int:forum_id>/json/', forum_views.forum_detail_json, name='forum_forum_detail_json'),
    path('yogforum/reply/<int:reply_id>/json/', forum_views.forum_reply_detail_json, name='forum_forum_reply_detail_json'),
]