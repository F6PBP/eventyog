from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/', auth_views.main, name='auth'),
    path('cart/', cart_views.main, name='cart'),
    path('yogevent/', event_views.main, name='yogevent'),
    path('detail-event', detail_event_views.main, name='detail-event-views'),
]