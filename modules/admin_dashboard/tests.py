from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from modules.main.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from django.contrib.messages import get_messages
from modules.authentication.forms import UserProfileForm
from django.contrib.auth.forms import UserCreationForm

class UserViewsTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            name='Admin User',
            email='admin@test.com',
            bio='Admin bio',
            role='AD',
            wallet=1000000
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            name='Regular User',
            email='user@test.com',
            bio='User bio',
            role='US',
            wallet=1000000
        )

        self.client = Client()

    def test_show_main_view_authenticated_admin(self):
        """Test show_main view for authenticated admin user"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard:main'))
        
        self.assertQuerySetEqual(
            response.context['users'].order_by('id'),
            UserProfile.objects.all().order_by('id'),
            transform=lambda x: x
        )

    def test_show_main_view_unauthenticated(self):
        """Test show_main view redirects unauthenticated users"""
        response = self.client.get(reverse('admin_dashboard:main'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth:login') + '?next=/admin-dashboard/')

    def test_search_users(self):
        """Test search_users functionality"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            reverse('admin_dashboard:search_user'),
            {'search': 'Regular'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fields']['name'], 'Regular User')

    def test_see_user_as_admin(self):
        """Test see_user view as admin"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(
            reverse('admin_dashboard:see_user', args=[self.regular_user.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user.html')
        self.assertEqual(response.context['user'], self.regular_user)
        self.assertEqual(response.context['user_profile'], self.user_profile)

    def test_see_user_as_regular_user(self):
        """Test see_user view as regular user (should redirect)"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(
            reverse('admin_dashboard:see_user', args=[self.regular_user.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:main'))

    def test_edit_user_successful(self):
        """Test successful user edit"""
        self.client.login(username='admin', password='adminpass123')
        updated_data = {
            'name': 'Updated Name',
            'bio': 'Updated bio',
            'email': 'updated@test.com',
            'wallet': '2000000',
            'username': 'updated_user',
            'categories': 'category1,category2'
        }
        
        response = self.client.post(
            reverse('admin_dashboard:edit_user', args=[self.regular_user.id]),
            updated_data
        )
        
        self.assertEqual(response.status_code, 302)
        updated_profile = UserProfile.objects.get(user=self.regular_user)
        self.assertEqual(updated_profile.name, 'Updated Name')
        self.assertEqual(updated_profile.email, 'updated@test.com')

    def test_delete_user_as_admin(self):
        """Test user deletion as admin"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(
            reverse('admin_dashboard:delete_user', args=[self.regular_user.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard:main'))
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.regular_user.id)

    def test_delete_user_as_regular_user(self):
        """Test user deletion attempt as regular user"""
        self.client.login(username='user', password='userpass123')
        response = self.client.post(
            reverse('admin_dashboard:delete_user', args=[self.regular_user.id])
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:main'))
        self.assertTrue(User.objects.filter(pk=self.regular_user.id).exists())

    def test_create_user_successful(self):
        # Simulate an uploaded image file
        profile_pic = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/jpeg'
        )
        """Test successful user creation"""
        self.client.login(username='admin', password='adminpass123')
        new_user_data = {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'profile_picture': profile_pic,
            'name': 'New User',
            'email': 'newuser@test.com',
            'bio': 'New user bio',
            'role': 'US'
        }
        
        response = self.client.post(reverse('admin_dashboard:create_user'), new_user_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_user_invalid_data(self):
        """Test user creation with invalid data"""
        self.client.login(username='admin', password='adminpass123')
        invalid_data = {
            'username': '',  # Invalid: empty username
            'password1': 'testpass123',
            'password2': 'different_password',  # Invalid: passwords don't match
            'name': 'New User',
            'email': 'invalid_email',  # Invalid email format
            'bio': 'New user bio',
            'wallet': 'not_a_number',  # Invalid: not a number
            'role': 'INVALID_ROLE'  # Invalid role
        }
        
        response = self.client.post(reverse('admin_dashboard:create_user'), invalid_data)
        
        self.assertEqual(response.status_code, 302)  # Redirects back due to invalid data
        self.assertFalse(User.objects.filter(username='').exists())