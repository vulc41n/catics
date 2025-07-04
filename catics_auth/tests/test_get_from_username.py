from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from catics_auth.models import Validation
from ..models import RegisterChallenge
from .constants import EMAIL, USERNAME, PASSWORD, CHALLENGE_TOKEN, CHALLENGE_ANSWER

User = get_user_model()

class GetFromUsernameTestCase(APITestCase):
    def setUp(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.REGISTER_CHALLENGE_EXPIRATION,
        ).id
        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'email': EMAIL,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL, 'password': PASSWORD },
        )
        self.user = User.objects.get(username=USERNAME)
        Validation.objects.create(
            user=self.user,
            expire_at=timezone.now(),
            validation_code='',
            is_validated=True,
        )
        response = self.client.post(
            reverse('auth-login'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data['token'])

    def test_unlogged(self):
        self.client.credentials()
        response = self.client.get(
            reverse('auth-get_from_username'),
            { 'username': USERNAME },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')

    def test_unvalidated(self):
        Validation.objects.filter(user=self.user).update(is_validated=False)
        self.test_basic()

    def test_basic(self):
        response = self.client.get(
            reverse('auth-get_from_username'),
            { 'username': USERNAME },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], self.user.id)


