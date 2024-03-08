"""
This file contains all the admins for rosters module
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from rosters.models import Roster, RosterManager, RosterUserSchedule


@admin.register(Roster)
class RosterAdmin(ModelAdmin):
    list_display = ("id", "title", "is_active")
    search_fields = ("title",)
    list_filter = ("is_active",)


@admin.register(RosterUserSchedule)
class RosterUserScheduleAdmin(ModelAdmin):
    list_display = (
        "id",
        "roster",
        "user",
        "working_day",
        "shift",
        "start_time",
        "end_time",
    )
    search_fields = ("roster__title", "user__email")
    list_filter = ("working_day", "shift", "roster__title")


@admin.register(RosterManager)
class RosterManagerAdmin(ModelAdmin):
    list_display = ("id", "roster", "manager")
    search_fields = ("roster__title", "manager__email")
