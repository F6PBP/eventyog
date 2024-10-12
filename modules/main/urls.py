from django.urls import path
from modules.main.views import *

app_name = 'main'

urlpatterns = [
    path('', main, name='main'),
    path('about', about, name='about'),
]