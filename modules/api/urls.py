from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('cart/', cart_views.main, name='cart'),
    path('auth/logout/', auth_views.logout, name='auth_logout'),
    path('auth/profile/', auth_views.profile, name='auth_profile'),
    # path('cart/', cart_views.main, name='cart'),                 # Halaman utama keranjang (opsional)
    path('cart/update/', cart_views.update_cart, name='update_cart'),  # Untuk memperbarui keranjang
    path('cart/checkout/', cart_views.checkout, name='checkout'),      # Untuk proses checkout
    path('cart/empty/', cart_views.empty_cart, name='empty_cart'),      # Untuk mengosongkan keranjang
]   
