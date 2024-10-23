from django.urls import path
from modules. registered_event.views import *

app_name = 'registered_event'

urlpatterns = [
    path('', main, name='main'),
]