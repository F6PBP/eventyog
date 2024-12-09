from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views, friend_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path('auth/profile/', auth_views.profile, name='auth_profile'),
    path('auth/profile/edit/', auth_views.edit_profile, name='auth_profile_edit'),
    path('auth/onboarding/', auth_views.onboarding, name='auth_onboarding'),
    
    path('friend/list/', friend_views.show_list, name='friend_list'),
    path('friend/<str:user_id>/', friend_views.main, name='friend_main'),
    path('friend/add/<str:friend_id>', friend_views.add_friend_ajax, name='friend_add'),
    path('friend/remove/<str:friend_id>', friend_views.remove_friend, name='friend_remove'),
]