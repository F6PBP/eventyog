from django.test import TestCase, Client
from django.urls import reverse
from modules.main.models import Event, UserProfile, Rating
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from datetime import datetime
import json

class EventViewTests(TestCase):
    def setUp(self):
        # Setup user, profile, and client
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.create(user=self.user, role='AD')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        # Setup an event instance
        self.event = Event.objects.create(
            title="Test Event",
            description="Event Description",
            category="Workshop",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            location="Test Location",
        )

    # Test case 1: Main view renders successfully with the event
    def test_main_view(self):
        response = self.client.get(reverse('yogevent:main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")

    # Test case 2: Main view filters by query
    def test_main_view_with_query_filter(self):
        response = self.client.get(reverse('yogevent:main') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")

    # Test case 3: Main view filters by category
    def test_main_view_with_category_filter(self):
        response = self.client.get(reverse('yogevent:main') + '?category=Workshop')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Event")

    # Test case 4: JSON response for show_event_json
    def test_show_event_json(self):
        response = self.client.get(reverse('yogevent:show_event_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    # Test case 5: XML response for show_event_xml
    def test_show_event_xml(self):
        response = self.client.get(reverse('yogevent:show_event_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')  # Change as needed if XML is different
        self.assertIn("Test Event", response.content.decode('utf-8'))

    # Test case 6: JSON response for event by ID
    def test_show_json_event_by_id(self):
        response = self.client.get(reverse('yogevent:show_json_event_by_id', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data[0]['fields']['title'], "Test Event")

    # Test case 7: Create event through AJAX with valid data
    def test_create_event_entry_ajax_valid(self):
        start_time = timezone.make_aware(datetime(2023, 10, 27, 10, 0, 0))
        data = {
            'title': 'New Event',
            'description': 'New Description',
            'category': 'Olahraga',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'location': 'New Location',
            'image_url': 'https://example.com/image.jpg'
        }
        response = self.client.post(reverse('yogevent:create_event_entry_ajax'), data, content_type='application/json')
        json_response = json.loads(response.content)
        self.assertTrue(json_response['status'])
        self.assertEqual(response.status_code, 200)

    # Test case 8: Create event through AJAX with missing title
    def test_create_event_entry_ajax_missing_title(self):
        data = {
            'title': '',
            'description': 'New Description',
            'category': 'Workshop',
            'start_time': timezone.now().isoformat(),
            'location': 'New Location',
            'image_url': 'https://example.com/image.jpg'
        }
        response = self.client.post(reverse('yogevent:create_event_entry_ajax'), data, content_type='application/json')
        json_response = json.loads(response.content)
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['message'], 'Invalid input')
        self.assertEqual(response.status_code, 200)

    # Test case 9: Delete an event and check if deleted
    def test_delete_event(self):
        response = self.client.post(reverse('yogevent:delete_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
        self.assertFalse(Event.objects.filter(uuid=self.event.uuid).exists())

    # Test case 10: Add a rating to an event
    def test_add_rating(self):
        data = {'rating': '5', 'review': 'Great event!'}
        response = self.client.post(reverse('yogevent:add_rating', args=[self.event.uuid]), data)
        json_response = json.loads(response.content)
        self.assertTrue(json_response['status'])
        self.assertEqual(json_response['message'], 'Rating submitted successfully!')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rating.objects.filter(rated_event=self.event).count(), 1)
