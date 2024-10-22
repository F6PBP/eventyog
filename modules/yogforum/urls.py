from django.urls import path
from modules.yogforum.views import *

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),
]