from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import jwt

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            role='VISUALIZADOR'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            role='ADMIN'
        )
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.me_url = reverse('user-me')
        self.user_list_url = reverse('user-list-create')

    def test_token_contains_role(self):
        data = { 'email': 'test@example.com', 'password': 'testpassword123' }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.data['access']
        payload = jwt.decode(access, options={"verify_signature": False})
        self.assertEqual(payload['role'], 'VISUALIZADOR')
        self.assertEqual(payload['email'], 'test@example.com')

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        self.client.force_authenticate(user=self.admin)
        data = { 
            'email': 'new@example.com', 'username': 'new', 'password': '123', 'role': 'GESTOR'
        }
        response = self.client.post(self.user_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(email='new@example.com').first().role, 'GESTOR')

    def test_create_user_sets_password(self):
        self.client.force_authenticate(user=self.admin)
        data = { 
            'email': 'pass@example.com', 'username': 'pass', 'password': 'securepass', 'role': 'ANALISTA'
        }
        response = self.client.post(self.user_list_url, data, format='json')
        u = User.objects.get(email='pass@example.com')
        self.assertTrue(u.check_password('securepass'))

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
