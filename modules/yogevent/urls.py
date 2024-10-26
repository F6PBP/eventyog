from django.urls import path
from modules.yogevent.views import *

app_name = 'yogevent'

urlpatterns = [
    path('', main, name='main'),
    path('get-event/', get_events_by_queries, name='get_event'),
    path('xml/', show_event_xml, name='show_xml'),
    path('json/', show_event_json, name='show_json'),
    path('xml/<str:id>/', show_xml_event_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_event_by_id, name='show_json_by_id'),
    path('detail-event/<uuid:uuid>/', detail_event, name='detail_event'),
    path('edit-event/<uuid:uuid>/', edit_event, name='edit_event'),
    path('delete-event/<uuid:uuid>/', delete_event, name='delete_event'),
    path('create-event/', create_event_entry_ajax, name="create_event_entry_ajax"),
    path('event-rate/<uuid:event_id>/', create_rating_event, name='create_rating_event'),
    path('add-rating/<uuid:event_id>/', add_rating, name='add_rating'),
    path('load-ratings/<uuid:event_id>/', load_event_ratings, name='load_event_ratings'),
    path('get-rating-event/<uuid:uuid>/', get_rating_event, name='get_rating_event'),
    path('book-event', book_event, name='book_event'),
    path('cancel-book', book_event, name='cancel_book'),
]