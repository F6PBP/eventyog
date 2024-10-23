from django.urls import path
from modules.yogpost.views import *

app_name = 'yogpost'

urlpatterns = [
    path('', show_forum, name='main'),
]