from django.urls import path
from modules.authentication.views import *

app_name = 'auth'

urlpatterns = [
    path('/login', login_user, name='login'),
    path('/logout', logout_user, name='logout'),
    path('/register', register, name='register'),
    path('/onboarding', onboarding, name='onboarding'),
    path('/profile', profile, name='profile'),
    path('/profile/edit', edit_profile, name='edit_profile'),
    path('/delete-profile', delete_profile, name='delete_profile')
]