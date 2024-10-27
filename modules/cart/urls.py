from django.urls import path
from modules.cart.views import *

app_name = 'cart'

urlpatterns = [
    path('', main, name='main'),
    path('checkout/', checkout , name='checkout'),
    path('empty_cart/', empty_cart, name='empty_cart'),
]