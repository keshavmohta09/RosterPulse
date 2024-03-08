"""
This file contains all the urls used for attendance module
"""

from django.urls import path

from attendance.apis import attendance

urlpatterns = [
    path("", attendance.CreateAttendanceAPI.as_view(), name="attendance-create")
]
