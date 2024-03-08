"""
This file contains all the model serializers for rosters module.
"""

from rest_framework import serializers

from rosters.models import Roster, RosterUserSchedule


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roster
        exclude = Roster.LOG_FIELDS


class RosterUserScheduleSerializer(serializers.ModelSerializer):
    working_day = serializers.SerializerMethodField()
    shift = serializers.SerializerMethodField()

    def get_working_day(self, instance):
        return RosterUserSchedule.WorkingDay(instance.working_day).label

    def get_shift(self, instance):
        return RosterUserSchedule.Shift(instance.shift).label

    class Meta:
        model = RosterUserSchedule
        exclude = RosterUserSchedule.LOG_FIELDS
