from django.urls import path
from modules.cart.views import *
from . import views

app_name = 'cart'

urlpatterns = [
    path('', main, name='main'),
    path('checkout/', views.checkout, name='checkout'),
]