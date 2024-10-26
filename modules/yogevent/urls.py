from django.urls import path
from modules.yogevent.views import *

app_name = 'yogevent'

urlpatterns = [
    path('', main, name='main'),
    path('xml/', show_event_xml, name='show_xml'),
    path('json/', show_event_json, name='show_json'),
    path('xml/<str:id>/', show_xml_event_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_event_by_id, name='show_json_by_id'),
    path('detail-event/<uuid:uuid>/', detail_event, name='detail_event'),
    path('edit-event/<uuid:uuid>/', edit_event, name='edit_event'),
    path('delete-event/<uuid:uuid>/', delete_event, name='delete_event'),
    path('create-event/', create_event_entry_ajax, name="create_event_entry_ajax"),
    path('add-rating/<uuid:event_id>/', add_rating, name='add_rating'),
    path('rate/<uuid:event_id>/', rate_event, name='rate_event'), 
    path('edit/<int:id>/', edit_merchandise, name='edit_merchandise'),
    path('delete/<int:id>/', delete_merchandise, name='delete_merchandise'),
    path('add_merchandise_ajax/', create_merchandise_ajax, name='create_merchandise_ajax'),
    path('show/', showMerch_json, name='showMerch_json'),
]