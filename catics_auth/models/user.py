from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class CaticsUser(AbstractUser):
    class Meta:
        db_table = "auth_user"

    email = models.EmailField(unique=True, blank=False, null=False)
    REQUIRED_FIELDS = ['email']

    def clean(self):
        if self.email is None or len(self.email) == 0:
            raise ValidationError({
                'email': 'Veuillez renseigner une adresse e-mail',
            })
        self.super().clean()
