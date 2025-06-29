import hashlib
import random
import string
from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import login, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import permissions, serializers
from rest_framework.response import Response
from knox.views import LoginView as KnoxLoginView
from ..models import Registration, RegisterChallenge
from .exceptions import ChallengeForAnotherEmailException, ChallengeFailException

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    challenge_id = serializers.PrimaryKeyRelatedField(queryset=RegisterChallenge.objects.all())
    challenge_answer = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'challenge_id', 'challenge_answer')

    def validate_password(self, value):
        validate_password(value)
        return value

class RegisterView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        # check challenge
        if data['challenge_id'].email != data['email']:
            raise ChallengeForAnotherEmailException()
        digest = hashlib.sha256(
            (data['challenge_id'].challenge + data['challenge_answer']).encode()
        ).hexdigest()
        if not digest.startswith("000000"):
            raise ChallengeFailException()
        
        user = User.objects.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password'],
        )
        code = ''.join(
                random.choice(string.ascii_lowercase)
                for _ in range(settings.EMAIL_VALIDATION_SIZE)
            )
        Registration.objects.create(
            user=user,
            expire_at=timezone.now() + settings.EMAIL_VALIDATION_EXPIRATION,
            validation_code=code,
        )
        mail.send_mail(
            from_email=settings.EMAIL_FROM,
            recipient_list=[user.email],
            subject=settings.EMAIL_VALIDATION_SUBJECT,
            message=settings.BASE_URL + reverse('auth-validate', query={
                'email': user.email,
                'code': code,
            })
        )
        login(request, user)
        return super(RegisterView, self).post(request)

