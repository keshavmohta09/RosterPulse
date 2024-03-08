"""
This file contains all the admins for attendance module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from attendance.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ("id", "roster_user_schedule", "image")
    search_fields = (
        "roster_user_schedule__user__email",
        "roster_user_schedule__roster__title",
    )
