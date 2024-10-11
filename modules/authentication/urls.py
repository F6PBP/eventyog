from django.urls import path
from modules.authentication.views import *

app_name = 'auth'

urlpatterns = [
    path('login', login_user, name='login'),
    path('logout', logout_user, name='logout'),
    path('register', register, name='register'),
    path('profile', profile, name='profile')
]