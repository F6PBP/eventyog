from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views, friend_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('yogforum/', forum_views.main, name='main'),
    path('yogforum/post/<int:post_id>/', forum_views.viewforum, name='viewforum'),
    path('yogforum/add-post/', forum_views.add_post, name='add_post'),
    path('yogforum/post/<int:post_id>/delete/', forum_views.delete_post, name='delete_post'),
    path('yogforum/reply/<int:reply_id>/delete/', forum_views.delete_reply, name='delete_reply'),
    path('yogforum/post/<int:post_id>/add_reply/', forum_views.add_reply, name='add_reply'),
    path('yogforum/reply/<int:reply_id>/', forum_views.view_reply_as_post, name='view_reply_as_post'), 
    path('yogforum/edit/<int:post_id>/', forum_views.edit_post, name='edit_post'),
    path('yogforum/like_post/<int:id>/', forum_views.like_post, name='like_post'),
    path('yogforum/dislike_post/<int:id>/', forum_views.dislike_post, name='dislike_post'),
    path('yogforum/like_reply/<int:id>/', forum_views.like_reply, name='like_reply'),
    path('yogforum/dislike_reply/<int:id>/', forum_views.dislike_reply, name='dislike_reply'),
    path('yogforum', forum_views.search_forum, name='search_forum'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path('auth/profile/', auth_views.profile, name='auth_profile'),
    path('auth/profile/edit/', auth_views.edit_profile, name='auth_profile_edit'),
    path('auth/onboarding/', auth_views.onboarding, name='auth_onboarding'),
    path('cart/get_cart_data/', cart_views.get_cart_data, name='get_cart_data'),
    path('cart/update/', cart_views.update_cart, name='update_cart'),  # Untuk memperbarui keranjang
    path('cart/checkout/', cart_views.checkout, name='checkout'),      # Untuk proses checkout
    path('cart/empty/', cart_views.empty_cart, name='empty_cart'),      # Untuk mengosongkan keranjang
    path('cart/empty_cart/', cart_views.empty_cart, name='empty_cart'),      # Untuk mengosongkan keranjang
    
    path('friend/list/', friend_views.show_list, name='friend_list'),
    path('friend/<str:user_id>/', friend_views.main, name='friend_main'),
    path('friend/add/<str:friend_id>', friend_views.add_friend_ajax, name='friend_add'),
    path('friend/remove/<str:friend_id>', friend_views.remove_friend, name='friend_remove'),
]