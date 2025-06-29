from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .constants import USERNAME, PASSWORD

User = get_user_model()

class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USERNAME, password=PASSWORD)

    def test_basic(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        token1 = response.data['token']
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        token2 = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token1)
        response = self.client.post(reverse('auth-logout'))
        self.assertEqual(response.status_code, 204)
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token2)
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 200)

    def test_logout_all(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        token1 = response.data['token']
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        token2 = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token1)
        response = self.client.post(reverse('auth-logoutall'))
        self.assertEqual(response.status_code, 204)
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token2)
        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 401)
