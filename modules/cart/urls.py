from django.urls import path
from modules.cart.views import *

app_name = 'cart'

urlpatterns = [
    path('', main, name='main'),
]