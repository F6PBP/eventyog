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
    path('admin/', admin_views.show_main, name='show_main'),
    path('admin/see_user/<str:username>', admin_views.see_user, name='see_user'),
    path('admin/delete_user/<str:username>', admin_views.delete_user, name='delete_user'),
    path('admin/edit_user/<str:username>', admin_views.edit_user, name='edit_user'),
    path('admin/create_user/', admin_views.create_user, name='create_user'),

    path('yogevent/main/', event_views.main, name='yogevent_main'),
    path('yogevent/events/', event_views.show_event_json, name='event_list_json'),
    path('yogevent/create/', event_views.create_event_flutter, name='yogevent_create'),
    path('yogevent/delete/<uuid:event_id>/', event_views.delete_event_flutter, name='delete_event_flutter'),    
    path('yogevent/update/<uuid:event_id>/', event_views.edit_event_flutter, name='edit_event_flutter'),
    path('yogevent/<uuid:event_id>/', event_views.show_event_by_id, name='show_event_by_id'),   
    path('yogevent/rate/<uuid:event_id>/', detail_event_views.add_rating, name='add_rating'),
    path('yogevent/buy-ticket-flutter/', detail_event_views.buy_ticket_flutter, name='buy_ticket_flutter'),
    path('yogevent/book-free-ticket/', detail_event_views.book_free_ticket_flutter, name='book_free_ticket'),
    path('yogevent/cancel-free-booking/', detail_event_views.cancel_free_booking, name='cancel_free_booking'),
    path('yogevent/tickets/<uuid:event_id>/', detail_event_views.get_tickets, name='get_tickets'),
    path('yogevent/user-ticket/<uuid:event_id>/', detail_event_views.get_user_ticket_status, name='get_user_ticket_status'),
    path('yogevent/upcoming-events/', event_views.show_upcoming_events, name='upcoming_events'),
    path('yogevent/add-event-to-cart/', detail_event_views.add_event_to_cart, name='add_event_to_cart'),
    path('yogevent/check-ticket-cart/<uuid:event_id>/', detail_event_views. check_ticket_in_cart, name=' check_ticket_in_cart'),

    # path('cart/', cart_views.main, name='cart'),                 # Halaman utama keranjang (opsional)
    path('cart/get_cart_data/', cart_views.get_cart_data, name='get_cart_data'),
    path('cart/update/', cart_views.update_cart, name='update_cart'),  # Untuk memperbarui keranjang
    path('cart/checkout/', cart_views.checkout, name='checkout'),      # Untuk proses checkout
    path('cart/empty/', cart_views.empty_cart, name='empty_cart'),      # Untuk mengosongkan keranjang
    path('cart/empty_cart/', cart_views.empty_cart, name='empty_cart'),      # Untuk mengosongkan keranjang
    path('auth/profile/edit/', auth_views.edit_profile, name='auth_profile_edit'),
    path('auth/onboarding/', auth_views.onboarding, name='auth_onboarding'),

    path('friend/list/', friend_views.show_list, name='friend_list'),
    path('friend/<str:user_id>/', friend_views.main, name='friend_main'),
    path('friend/add/<str:friend_id>', friend_views.add_friend_ajax, name='friend_add'),
    path('friend/remove/<str:friend_id>', friend_views.remove_friend, name='friend_remove'),

    path('merchandise/', merchandise_views.main, name='merchandise_main'),
    path('merchandise/<int:id>/', merchandise_views.show_merchandise_by_id, name='merchandise_detail'),
    path('merchandise/create/', merchandise_views.create_merchandise_ajax, name='merchandise_create'),
    path('merchandise/add-to-cart/', merchandise_views.add_items_to_cart, name='merchandise_add_to_cart'),
    path('merchandise/edit/<int:id>/', merchandise_views.edit_merchandise, name='merchandise_edit'),
    path('merchandise/delete/<int:id>/', merchandise_views.delete_merchandise, name='merchandise_delete'),
    path('merchandise/show/<str:event_id>/', merchandise_views.showMerch_json, name='merchandise_showMerch_json'),
]
