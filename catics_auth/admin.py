from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Registration, CaticsUser

admin.site.register(Registration)
admin.site.register(CaticsUser, UserAdmin)
