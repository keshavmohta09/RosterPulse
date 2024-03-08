"""
This file contains all the admins for users module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from users.models import Profile, User, UserRole


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("id", "user", "phone_number")
    search_fields = ("user__email",)


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("id", "user", "role")
    search_fields = ("user__email",)
    list_filter = ("role",)
