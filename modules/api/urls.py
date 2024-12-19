from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path('auth/profile/', auth_views.profile, name='auth_profile'),

    path('yogevent/main/', event_views.main, name='yogevent_main'),
    path('yogevent/events/', event_views.show_event_json, name='event_list_json'),
    path('yogevent/create/', event_views.create_event_flutter, name='yogevent_create'),
    path('yogevent/delete/<uuid:event_id>/', event_views.delete_event_flutter, name='delete_event_flutter'),    
    path('yogevent/update/<uuid:event_id>/', event_views.edit_event_flutter, name='edit_event_flutter'),
    path('yogevent/<uuid:event_id>/', event_views.show_event_by_id, name='show_event_by_id'),   
    path('yogevent/rate/<uuid:event_id>/', detail_event_views.add_rating, name='add_rating'),
    path('yogevent/buy-ticket-flutter/', detail_event_views.buy_ticket_flutter, name='buy_ticket_flutter'),
    path('yogevent/delete-user-ticket/', detail_event_views.delete_user_ticket, name='delete_user_ticket'),
    path('yogevent/tickets/<uuid:event_id>/', detail_event_views.get_tickets, name='get_tickets'),
    path('yogevent/user-ticket/<uuid:event_id>/', detail_event_views.get_user_ticket_status, name='get_user_ticket_status'),
    path('yogevent/user-cart/<uuid:event_id>/', detail_event_views.get_user_event_cart, name='get_user_event_cart'),
    path('yogevent/search/', event_views.search_events, name='search_events'),
]