from django.urls import path
from modules.cart.views import *

app_name = 'cart'

urlpatterns = [
    path('', main, name='main'),
    path('update-cart/<str:type>/<int:item_id>/<str:action>/', update_cart, name='update_cart'),
]