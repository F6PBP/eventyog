from django.urls import path
from .views import admin_views, auth_views, cart_views, detail_event_views, event_views, forum_views, merchandise_views, profile_views
app_name = 'api'

urlpatterns = [
    path('auth/login/', auth_views.login, name='auth_login'),
    path('auth/register/', auth_views.register, name='auth_register'),
    path('merchandise/', merchandise_views.main, name='merchandise_main'),
    path('merchandise/<int:id>/', merchandise_views.show_merchandise_by_id, name='merchandise_detail'),
    path('merchandise/create/', merchandise_views.create_merchandise_ajax, name='merchandise_create'),
    path('merchandise/add-to-cart/', merchandise_views.add_items_to_cart, name='merchandise_add_to_cart'),
    path('merchandise/edit/<int:id>/', merchandise_views.edit_merchandise, name='merchandise_edit'),
    path('merchandise/delete/<int:id>/', merchandise_views.delete_merchandise, name='merchandise_delete'),
    path('merchandise/show/<str:event_id>', merchandise_views.showMerch_json, name='merchandise_showMerch_json'),

]