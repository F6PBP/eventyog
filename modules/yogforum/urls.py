from django.urls import path
from modules.yogforum.views import *

app_name = 'yogforum'

urlpatterns = [
    path('', main, name='main'),  # Menampilkan semua post
    path('post/<int:post_id>/', viewforum, name='viewforum'),  # Menampilkan detail post berdasarkan ID
]