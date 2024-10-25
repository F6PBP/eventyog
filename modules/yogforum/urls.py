from django.urls import path
from modules.yogforum.views import main, viewforum, add_post, delete_post, delete_reply

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),
    path('post/<int:post_id>/', viewforum, name='viewforum'),
    path('add-post/', add_post, name='add_post'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', delete_reply, name='delete_reply'),
]