from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from modules.main.models import Merchandise
from decimal import Decimal
import json

class MerchandiseTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test merchandise
        self.test_merchandise = Merchandise.objects.create(
            name='Test Merchandise',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg'
        )

    def test_create_merchandise_ajax(self):
        """Test creating merchandise through AJAX"""
        merchandise_data = {
            'name': 'Ajax Merchandise',
            'description': 'Ajax Description',
            'price': '199.99',
            'image_url': 'https://example.com/ajax-image.jpg'
        }
        response = self.client.post(
            reverse('merchandise:create_merchandise_ajax'),
            merchandise_data
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'CREATED')

    def test_edit_merchandise(self):
        """Test editing existing merchandise"""
        updated_data = {
            'name': 'Updated Merchandise',
            'description': 'Updated Description',
            'price': '129.99',
            'image_url': 'https://example.com/updated-image.jpg'
        }
        response = self.client.post(
            reverse('merchandise:edit_merchandise', args=[self.test_merchandise.id]),
            updated_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        updated_merchandise = Merchandise.objects.get(id=self.test_merchandise.id)
        self.assertEqual(updated_merchandise.name, 'Updated Merchandise')

    def test_delete_merchandise(self):
        """Test deleting merchandise"""
        response = self.client.post(
            reverse('merchandise:delete_merchandise', args=[self.test_merchandise.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(
            Merchandise.objects.filter(id=self.test_merchandise.id).exists()
        )

    def test_invalid_merchandise_id(self):
        """Test accessing non-existent merchandise"""
        response = self.client.get(
            reverse('merchandise:showMerch_json', args=[99999])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_create_merchandise_invalid_data(self):
        """Test creating merchandise with invalid data"""
        invalid_data = {
            'name': '',  # Name should not be empty
            'price': 'not_a_number',  # Invalid price
            'image_url': 'not_a_url'  # Invalid URL
        }
        response = self.client.post(
            reverse('merchandise:create_merchandise'),
            invalid_data
        )
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertFalse(
            Merchandise.objects.filter(name='').exists()
        )

    def test_merchandise_model(self):
        """Test merchandise model fields and methods"""
        merchandise = Merchandise.objects.create(
            name='Test Model',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/test.jpg'
        )
        self.assertEqual(str(merchandise.name), 'Test Model')
        self.assertEqual(merchandise.price, Decimal('99.99'))
        self.assertTrue(merchandise.created_at)
        self.assertTrue(merchandise.updated_at)

    def test_update_merchandise_invalid_data(self):
        """Test updating merchandise with invalid data"""
        invalid_data = {
            'name': '',  # Name should not be empty
            'price': 'not_a_number',  # Invalid price
            'image_url': 'not_a_url'  # Invalid URL
        }
        response = self.client.post(
            reverse('merchandise:edit_merchandise', args=[self.test_merchandise.id]),
            invalid_data
        )
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        updated_merchandise = Merchandise.objects.get(id=self.test_merchandise.id)
        self.assertNotEqual(updated_merchandise.name, '')  # Name should not be updated

    def test_create_merchandise_without_login(self):
        """Test creating merchandise without being logged in"""
        self.client.logout()
        merchandise_data = {
            'name': 'Unauthorized Merchandise',
            'description': 'Unauthorized Description',
            'price': '149.99',
            'image_url': 'https://example.com/unauthorized-image.jpg'
        }
        response = self.client.post(
            reverse('merchandise:create_merchandise'),
            merchandise_data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_edit_merchandise_without_login(self):
        """Test editing merchandise without being logged in"""
        self.client.logout()
        updated_data = {
            'name': 'Unauthorized Update',
            'description': 'Unauthorized Description',
            'price': '129.99',
            'image_url': 'https://example.com/unauthorized-update.jpg'
        }
        response = self.client.post(
            reverse('merchandise:edit_merchandise', args=[self.test_merchandise.id]),
            updated_data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_delete_merchandise_without_login(self):
        """Test deleting merchandise without being logged in"""
        self.client.logout()
        response = self.client.post(
            reverse('merchandise:delete_merchandise', args=[self.test_merchandise.id])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to login