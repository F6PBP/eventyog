from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.main.models import UserProfile, Event
from datetime import datetime

User = get_user_model()

class EventViewTests(TestCase):
    def setUp(self):
        # Buat user dan user profile
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = UserProfile.objects.create(user=self.user, role='US')
        self.client.login(username='testuser', password='password')

        # Buat event
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event.',
            category='music',
            start_time=datetime(2024, 10, 30, 18, 0),
            end_time=datetime(2024, 10, 30, 20, 0),
            location='Test Location',
            image_urls=['https://via.placeholder.com/800x400']
        )

    def test_main_view(self):
        """Test if the main view is accessible and contains the event title."""
        response = self.client.get(reverse('yogevent:main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_main_views(self):
        response = self.client.get(reverse('yogevent:main'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_create_event_entry_ajax(self):
        """Test creating a new event via AJAX."""
        response = self.client.post(reverse('yogevent:create_event_entry_ajax'), {
            'title': 'New Event',
            'description': 'New event description',
            'category': 'music',
            'start_time': '2024-10-31 18:00:00',
            'end_time': '2024-10-31 20:00:00',
            'location': 'New Location',
            'image_urls': ['https://via.placeholder.com/800x400']
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': True, 'message': 'Event created successfully.'})
        self.assertTrue(Event.objects.filter(title='New Event').exists())

    def test_detailed_event(self):
        response = self.client.get(reverse('yogevent:detail_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_details_event(self):
        response = self.client.get(reverse('yogevent:detail_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_detail_event(self):
        """Test the detail view of an event."""
        response = self.client.get(reverse('yogevent:detail_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_edit_event(self):
        """Test editing an event."""
        response = self.client.post(reverse('yogevent:edit_event', args=[self.event.uuid]), {
            'title': 'Updated Event',
            'description': 'Updated description',
            'category': 'music',
            'start_time': '2024-10-31 18:00:00',
            'end_time': '2024-10-31 20:00:00',
            'location': 'Updated Location',
            'image_urls': ['https://via.placeholder.com/800x400']
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after saving
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event')

    def test_delete_event(self):
        """Test deleting an event."""
        response = self.client.post(reverse('yogevent:delete_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_detailed_event(self):
        response = self.client.get(reverse('yogevent:detail_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

    def test_deleted_event(self):
        response = self.client.post(reverse('yogevent:delete_event', args=[self.event.uuid]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_edited_event(self):
        """Test editing an event."""
        response = self.client.post(reverse('yogevent:edit_event', args=[self.event.uuid]), {
            'title': 'Updated Event',
            'description': 'Updated description',
            'category': 'music',
            'start_time': '2024-10-31 18:00:00',
            'end_time': '2024-10-31 20:00:00',
            'location': 'Updated Location',
            'image_urls': ['https://via.placeholder.com/800x400']
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after saving
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event')