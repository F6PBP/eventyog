from django.urls import path
from modules.admin_dashboard.views import *

app_name = 'admin_dashboard'

urlpatterns = [
    path('', show_main, name='main'),
    path('search-users', search_users, name='search_user'),
    path('user/<int:user_id>', see_user, name='see_user'),
    path('user/<int:user_id>/edit', edit_user, name='edit_user'),
    path('user/<int:user_id>/delete', delete_user, name='delete_user'),
]