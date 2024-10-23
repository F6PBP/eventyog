from django.urls import path
from modules.merchandise.views import *

app_name = 'merchandise'

urlpatterns = [
    path('', main, name='main'),
]