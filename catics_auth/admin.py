from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import RegisterChallenge, Validation, CaticsUser

admin.site.register(RegisterChallenge)
admin.site.register(Validation)
admin.site.register(CaticsUser, UserAdmin)
