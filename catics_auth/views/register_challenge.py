import random
import string
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import RegisterChallenge

class RegisterChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterChallenge
        fields = ('email',)

class RegisterChallengeView(APIView):
    def get(self, request, format=None):
        # we do not check if the email is taken so a bruteforcer cannot dump email addresses
        serializer = RegisterChallengeSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        challenge = ''.join(
                random.choice(string.ascii_lowercase)
                for _ in range(settings.REGISTER_CHALLENGE_SIZE)
            )
        challenge_id = RegisterChallenge.objects.create(
            challenge=challenge,
            email=data['email'],
            expire_at=timezone.now() + settings.REGISTER_CHALLENGE_EXPIRATION,
        ).id
        return Response({
            'id': challenge_id,
            'challenge': challenge,
        })
