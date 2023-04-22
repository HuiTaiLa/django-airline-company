from django.contrib import admin
from .models import User
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
# Register your models here.
# class UserProfileAdmin(UserAdmin, User):
#     readonly_fields = ('password',)

admin.site.register(User)
