from datetime import timedelta
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from knox.models import AuthToken
from knox.settings import CONSTANTS
from freezegun import freeze_time
from ..models import Registration, RegisterChallenge
from .constants import USERNAME, PASSWORD, EMAIL, CHALLENGE_TOKEN, CHALLENGE_ANSWER

class ValidateTestCase(APITestCase):
    def setUp(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
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
        self.token = response.data['token']
        token_start = self.token[:CONSTANTS.TOKEN_KEY_LENGTH]
        self.user = AuthToken.objects.filter(token_key=token_start) \
            .select_related('user') \
            .first() \
            .user
        self.registration = Registration.objects.get(user=self.user)
        self.validation_code = self.registration.validation_code

    def test_basic(self):
        response = self.client.get(
            reverse('auth-validate'),
            { 'email': EMAIL, 'code': self.validation_code },
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(reverse('auth-test-is_validated'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_expiration(self):
        with freeze_time(self.registration.expire_at + timedelta(seconds=1)):
            response = self.client.get(
                reverse('auth-validate'),
                { 'email': EMAIL, 'code': self.validation_code },
            )
            self.assertEqual(response.status_code, 410)
            self.assertEqual(response.data['detail'].code, 'expired')
            self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
            response = self.client.get(reverse('auth-test-is_validated'))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.data)

    def test_unusable(self):
        Registration.objects.filter(pk=self.registration.id).update(is_usable=False)
        response = self.client.get(
            reverse('auth-validate'),
            { 'email': EMAIL, 'code': self.validation_code },
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(reverse('auth-test-is_validated'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_case_sensitivity(self):
        response = self.client.get(
            reverse('auth-validate'),
            { 'email': EMAIL, 'code': self.validation_code.upper() },
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(reverse('auth-test-is_validated'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)

    def test_wrong_code(self):
        response = self.client.get(
            reverse('auth-validate'),
            {
                'email': EMAIL,
                'code': ''.join(str(i)[0] for i in range(settings.EMAIL_VALIDATION_SIZE))
            },
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(reverse('auth-test-is_validated'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_missing_email(self):
        response = self.client.get(
            reverse('auth-validate'),
            { 'code': self.validation_code },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'required')

    def test_missing_code(self):
        response = self.client.get(
            reverse('auth-validate'),
            { 'email': EMAIL },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'][0].code, 'required')

    def test_code_long(self):
        response = self.client.get(
            reverse('auth-validate'),
            {
                'email': EMAIL,
                'code': ''.join(str(i)[0] for i in range(settings.EMAIL_VALIDATION_SIZE + 1))
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'][0].code, 'max_length')

    def test_code_short(self):
        response = self.client.get(
            reverse('auth-validate'),
            {
                'email': EMAIL,
                'code': ''.join(str(i)[0] for i in range(settings.EMAIL_VALIDATION_SIZE - 1))
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'][0].code, 'min_length')
