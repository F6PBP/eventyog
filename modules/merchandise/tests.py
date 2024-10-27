from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from modules.main.models import Merchandise
from decimal import Decimal
import json

class MerchandiseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        self.test_merchandise = Merchandise.objects.create(
            name='Test Merchandise',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg'
        )

    def test_create_merchandise_ajax(self):
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
        self.assertEqual(response.status_code, 302)
        updated_merchandise = Merchandise.objects.get(id=self.test_merchandise.id)
        self.assertEqual(updated_merchandise.name, 'Updated Merchandise')

    def test_delete_merchandise(self):
        response = self.client.post(
            reverse('merchandise:delete_merchandise', args=[self.test_merchandise.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Merchandise.objects.filter(id=self.test_merchandise.id).exists()
        )

    def test_invalid_merchandise_id(self):
        response = self.client.get(
            reverse('merchandise:showMerch_json', args=[99999])
        )
        self.assertEqual(response.status_code, 302) 

    def test_create_merchandise_invalid_data(self):
        invalid_data = {
            'name': '',  
            'price': 'not_a_number',  
            'image_url': 'not_a_url'  
        }
        response = self.client.post(
            reverse('merchandise:create_merchandise'),
            invalid_data
        )
        self.assertEqual(response.status_code, 200) 
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
        invalid_data = {
            'name': '',  
            'price': 'not_a_number',  
            'image_url': 'not_a_url' 
        }
        response = self.client.post(
            reverse('merchandise:edit_merchandise', args=[self.test_merchandise.id]),
            invalid_data
        )
        self.assertEqual(response.status_code, 200) 
        updated_merchandise = Merchandise.objects.get(id=self.test_merchandise.id)
        self.assertNotEqual(updated_merchandise.name, '')  

    def test_create_merchandise_without_login(self):
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
        self.assertEqual(response.status_code, 302)  

    def test_edit_merchandise_without_login(self):
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
        self.assertEqual(response.status_code, 302) 

    def test_delete_merchandise_without_login(self):
        self.client.logout()
        response = self.client.post(
            reverse('merchandise:delete_merchandise', args=[self.test_merchandise.id])
        )
        self.assertEqual(response.status_code, 302)  