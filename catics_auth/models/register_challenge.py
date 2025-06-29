from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class RegisterChallenge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    challenge = models.CharField(max_length=settings.REGISTER_CHALLENGE_SIZE)
    email = models.EmailField(unique=True)


