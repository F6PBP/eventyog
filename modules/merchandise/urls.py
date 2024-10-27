from django.urls import path
from modules.merchandise.views import *

app_name = 'merchandise'

urlpatterns = [
    path('', main, name='main'),
    path('create/', create_merchandise, name='create_merchandise'),
    path('edit/<int:id>/', edit_merchandise, name='edit_merchandise'),
    path('delete/<int:id>/', delete_merchandise, name='delete_merchandise'),
    path('add_merchandise_ajax/', create_merchandise_ajax, name='create_merchandise_ajax'),
    path('show/', showMerch_json, name='showMerch_json'),
    path('show/<int:id>/', show_merchandise_by_id, name='showMerch_json'),
]