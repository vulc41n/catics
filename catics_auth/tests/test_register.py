import random
import string
import hashlib
from django.core import mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from ..models import RegisterChallenge
from .constants import USERNAME, PASSWORD, EMAIL, CHALLENGE_TOKEN, CHALLENGE_ANSWER

class RegisterTestCase(APITestCase):
    @staticmethod
    def solve_challenge(token: str) -> str:
        while True:
            answer = ''.join(
                    random.choice(string.ascii_lowercase)
                    for _ in range(6)
                )
            digest = hashlib.sha256((token + answer).encode()).hexdigest()
            if digest.startswith("000000"):
                return answer

    def test_basic(self):
        response = self.client.get(reverse('auth-register-challenge'), { 'email': EMAIL })
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertIn('challenge', response.data)
        challenge_id = response.data['id']
        challenge_token = response.data['challenge']
        challenge_answer = RegisterTestCase.solve_challenge(challenge_token)

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
        response = self.client.get(reverse('auth-register-challenge'), { 'email': 'notanemail' })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'invalid')
        self.assertEqual(len(mail.outbox), 0)

    def test_different_emails(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
        ).id
        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'email': 'anotheremail@test.fr',
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'challenge_for_another_email')
        self.assertEqual(len(mail.outbox), 0)

    def test_same_email(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
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
        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME + '2',
                'email': EMAIL,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'unique')
        self.assertEqual(len(mail.outbox), 1)

    def test_same_username(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
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
        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'email': 'anotheradress@test.fr',
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0].code, 'unique')
        self.assertEqual(len(mail.outbox), 1)

    def test_missing_username(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
        ).id
        response = self.client.post(
            reverse('auth-register'),
            {
                'email': EMAIL,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_email(self):
        challenge_id = RegisterChallenge.objects.create(
            challenge=CHALLENGE_TOKEN,
            email=EMAIL,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
        ).id
        response = self.client.get(reverse('auth-register-challenge'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(
            reverse('auth-register'),
            {
                'username': USERNAME,
                'password': PASSWORD,
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_password(self):
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
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0].code, 'required')
        self.assertEqual(len(mail.outbox), 0)

    def test_password_too_short(self):
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
                'password': '1aC',
                'challenge_id': challenge_id,
                'challenge_answer': CHALLENGE_ANSWER,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0].code, 'password_too_short')
        self.assertEqual(len(mail.outbox), 0)

    def test_wrong_challenge(self):
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
                'challenge_answer': CHALLENGE_ANSWER[:-1] + '!',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'challenge_fail')
        self.assertEqual(len(mail.outbox), 0)
