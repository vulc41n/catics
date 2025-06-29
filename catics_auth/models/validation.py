from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Validation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_usable = models.BooleanField(default=True)
    is_validated = models.BooleanField(default=False)
    validation_code = models.CharField(max_length=settings.EMAIL_VALIDATION_SIZE)

