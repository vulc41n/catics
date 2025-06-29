import os
import hashlib
from django.core import mail
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from .constants import USERNAME, PASSWORD, EMAIL

class RegisterTestCase(APITestCase):
    def test_basic(self):
        response = self.client.post(
            reverse('auth-register-request'),
            {},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertIn('challenge', response.data)
        challenge_id = response.data['id']
        challenge_token = response.data['challenge']

        while True:
            challenge_answer = os.urandom(4).hex()
            digest = hashlib.sha256((challenge_token + challenge_answer).encode()).hexdigest()
            if digest.startswith("0000"):
                break

        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'email': EMAIL,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': challenge_answer,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, settings.EMAIL_VALIDATION_SUBJECT)

        response = self.client.get(reverse('auth-test-am_i_logged'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('auth-test-is_validated'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_wrong_email(self):
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': 'notanemail', 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'invalid')
        self.assertEqual(len(mail.outbox), 0)

    def test_same_email(self):
        self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL, 'password': PASSWORD },
        )
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME + '2', 'email': EMAIL, 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'unique')
        self.assertEqual(len(mail.outbox), 1)

    def test_same_username(self):
        self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL, 'password': PASSWORD },
        )
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': 'anotheradress@test.fr', 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0].code, 'unique')
        self.assertEqual(len(mail.outbox), 1)

    def test_missing_username(self):
        response = self.client.post(
            reverse('auth-register'),
            { 'email': EMAIL, 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_email(self):
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'password': PASSWORD },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_password(self):
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_password_too_short(self):
        response = self.client.post(
            reverse('auth-register'),
            { 'username': USERNAME, 'email': EMAIL, 'password': '1aC' },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0].code, 'password_too_short')
        self.assertEqual(len(mail.outbox), 0)
