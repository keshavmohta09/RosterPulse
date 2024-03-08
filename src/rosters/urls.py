"""
This file contains all the urls used for rosters module
"""

from django.urls import path

from rosters.apis import roster, roster_user_schedule

urlpatterns = [
    path("", roster.CreateRosterAPI.as_view(), name="roster-create"),
    path("list/", roster.ListRosterAPI.as_view(), name="roster-list"),
    path(
        "users/schedules/",
        roster_user_schedule.CreateRosterUserScheduleAPI.as_view(),
        name="roster-user-schedule-create",
    ),
    path(
        "users/schedules/list/",
        roster_user_schedule.ListRosterUserScheduleAPI.as_view(),
        name="roster-user-schedule-list",
    ),
    path(
        "users/schedules/<int:pk>/",
        roster_user_schedule.UpdateRosterUserScheduleAPI.as_view(),
        name="roster-user-schedule-update",
    ),
]
