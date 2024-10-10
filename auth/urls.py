from django.urls import path
from auth.views import *

app_name = 'auth'

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('onboarding', onboarding, name='onboarding')
]