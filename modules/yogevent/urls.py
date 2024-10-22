from django.urls import path
from modules.yogevent.views import *

app_name = 'yogevent'

urlpatterns = [
    path('', main, name='main'),
]