from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import Validation
from .exceptions import ExpiredException

User = get_user_model()

class ValidateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=settings.EMAIL_VALIDATION_SIZE)

    def validate_code(self, value):
        if len(value) < settings.EMAIL_VALIDATION_SIZE:
            raise ValidationError('Le code doit contenir 8 caractères', code='min_length')
        return value

class ValidateView(APIView):
    def get(self, request, format=None):
        serializer = ValidateSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data
        
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            # avoid bruteforce to get emails
            return Response(True)

        validations = Validation.objects.filter(
                user=user,
                is_usable=True,
                validation_code=data['code'].lower(),
            )
        validation = validations.first()
        if validation is None:
            # avoid bruteforce to get emails
            return Response(True)
        if validation.expire_at < timezone.now():
            raise ExpiredException()
        validations.update(is_validated=True, is_usable=False)
        return Response(True)

