"""
This file contains all the model serializers for attendance module.
"""

from rest_framework import serializers

from attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        exclude = Attendance.LOG_FIELDS
