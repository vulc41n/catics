from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from .constants import EMAIL, USERNAME, PASSWORD

User = get_user_model()

class LoginTestCase(APITestCase):
    def setUp(self):
        self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL, 'password': PASSWORD },
        )
        self.user = User.objects.get(username=USERNAME)

    def test_basic(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 200)

    def test_wrong_username(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'incorrect', 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0].code, 'authorization')
        self.assertNotIn('token', response.data)

    def test_wrong_password(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': 'incorrect' },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0].code, 'authorization')
        self.assertNotIn('token', response.data)

    def test_unlogged(self):
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
