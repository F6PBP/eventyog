from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path('auth/profile/', auth_views.profile, name='auth_profile'),
    path('yogevent/', event_views.create_event_flutter, name='yogevent'),
    path('detail-event-rating/', detail_event_views.create_rating_flutter, name='detail-event-views'),
    path('detail-event-ticket/', detail_event_views.buy_ticket_flutter, name='detail-event-ticket'),
]