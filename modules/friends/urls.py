from django.urls import path
from modules.friends.views import *

app_name = 'friends'

urlpatterns = [
    path('', show_list, name='show_list'),
    path('<int:user_id>', main, name='main'),
    path('add_friend_ajax/<int:friend_id>', add_friend_ajax, name='add_friend_ajax'),
    path('remove_friend_ajax/<int:friend_id>', remove_friend, name='remove_friend'),
]