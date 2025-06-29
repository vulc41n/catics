from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from ..models import RegisterChallenge
from .constants import EMAIL, USERNAME, PASSWORD, CHALLENGE_TOKEN, CHALLENGE_ANSWER

User = get_user_model()

class LoginTestCase(APITestCase):
    def setUp(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.REGISTER_CHALLENGE_EXPIRATION,
        ).id
        self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'email': EMAIL,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
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
