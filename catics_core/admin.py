from django.contrib import admin
from .models import Agent, AgentVersion, Game

admin.site.register(Agent)
admin.site.register(AgentVersion)
admin.site.register(Game)
