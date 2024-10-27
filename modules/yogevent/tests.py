from django.test import TestCase, Client
from modules.main.models import Event


class mainTest(TestCase):
    def test_login_template(self):
        c = Client()
        response = c.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_register_template(self):
        c = Client()
        response = c.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        
    def test_onboarding_template(self):
        dekdepe = User.objects.create_user(username='dekdepe', password='dekdepe')
        c = Client()
        response = c.get('/auth/onboarding', request={
            'user': dekdepe
        })
        # Redirecting        
        self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        c = Client()
        response = c.get('/auth/logout')
        self.assertEqual(response.status_code, 302)
        
    def test_login_for_unregistered_user(self):
        user_data = {
            'username': 'gadadidb',
            'password': 'gadadidb'
        }
        
        response = self.client.post(reverse('auth:login'), user_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_login_for_registered_user(self):
        user_data = {
            'username': 'dekdepe',
            'password': 'dummy123'
        }
        
        response = self.client.post(reverse('auth:login'), user_data)
        
        self.assertEqual(response.status_code, 200)
    def test_register_user(self):
        user_data = {
            'username': 'dekdepe',
            'password1': 'dummy123',
            'password2': 'dummy123'
        }
        
        response = self.client.post(reverse('auth:register'), user_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/auth/onboarding')
    
    def test_password_mismatch(self):
        user_data = {
            'username': 'dekdepe',
            'password1': 'dummy123',
            'password2': 'dummy1234'
        }
        
        response = self.client.post(reverse('auth:register'), user_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The two password fields didn’t match.')
        
    
    def test_profile_page(self):
        dekdepe = User.objects.create_user(username='dekdepe', password='dekdepe')
        dekdepe_profile = UserProfile.objects.create(
            user=dekdepe,
            name='Dek Depe',
            email='dekdepe@gmail.com',
            bio='I am a cool person',
            role=UserRoles.USER,
            categories=''
        )
        
        c = Client()
        c.force_login(dekdepe)
        
        response = c.get('/auth/profile', request={
            'user_profile': dekdepe_profile
        })
        
        self.assertEqual(response.status_code, 200)