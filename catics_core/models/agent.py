from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Agent(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=settings.NAMES_MAX_SIZE)
