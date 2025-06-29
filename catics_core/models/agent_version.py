from django.db import models
from django.conf import settings
from . import Agent

class AgentVersion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(default=0)
    wasm = models.BinaryField(max_length=settings.WASM_MAX_SIZE)
