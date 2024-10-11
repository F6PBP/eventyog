from django.urls import path
from modules.authentication.views import *

app_name = 'main'

urlpatterns = [
    path('', login, name='main'),
]