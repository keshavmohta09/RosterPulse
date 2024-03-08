"""
This file contains all the APIs related to roster user schedule model
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView

from rosters.models import Roster, RosterManager, RosterUserSchedule
from rosters.serializers import RosterSerializer, RosterUserScheduleSerializer
from rosters.services import (
    bulk_create_roster_user_schedules,
    delete_roster_user_schedule,
    update_roster_user_schedule,
)
from users.constants import OBJECT_NOT_FOUND
from users.models import User
from users.permissions import IsManager, IsStaffMember
from users.serializers import UserSerializer
from utils.response import CustomResponse


class CreateRosterUserScheduleAPI(APIView):
    """
    This API is used to add a new roster schedule for a user
    Response codes: 201, 400, 404
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):
        roster = serializers.IntegerField()
        user = serializers.IntegerField()
        working_day = serializers.ChoiceField(
            choices=RosterUserSchedule.WorkingDay.labels
        )
        shift = serializers.ChoiceField(choices=RosterUserSchedule.Shift.labels)
        start_time = serializers.TimeField()
        end_time = serializers.TimeField()

        def validate_working_day(self, value):
            for choice, label in RosterUserSchedule.WorkingDay.choices:
                if label == value:
                    return choice

        def validate_shift(self, value):
            for choice, label in RosterUserSchedule.Shift.choices:
                if label == value:
                    return choice

    class OutputSerializer(RosterUserScheduleSerializer):

        class RosterOutputSerializer(RosterSerializer):
            class Meta:
                model = Roster
                fields = ("id", "title")

        class UserOutputSerializer(UserSerializer):
            full_name = serializers.CharField()

            class Meta:
                model = User
                fields = ("id", "full_name")

        roster = RosterOutputSerializer()
        user = UserOutputSerializer()

        class Meta:
            fields = (
                "id",
                "roster",
                "user",
                "shift",
                "working_day",
                "start_time",
                "end_time",
            )
            model = RosterUserSchedule

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

        if not RosterManager.objects.filter(
            date_deleted__isnull=True, roster_id=validated_data["roster"]
        ).exists():
            return CustomResponse(
                errors=OBJECT_NOT_FOUND.format(object="Roster manager"),
                status=HTTP_404_NOT_FOUND,
            )

        # Creating new roster user schedule
        success, roster_user_schedules = bulk_create_roster_user_schedules(
            roster=validated_data.pop("roster"), data=[validated_data]
        )
        if not success:
            return CustomResponse(
                errors=roster_user_schedules, status=HTTP_400_BAD_REQUEST
            )

        return CustomResponse(
            data=self.OutputSerializer(instance=roster_user_schedules[0]).data,
            status=HTTP_201_CREATED,
        )


class UpdateRosterUserScheduleAPI(APIView):
    """
    This API is used to update the roster schedule for a user
    Response codes: 200, 400, 404
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):
        user = serializers.IntegerField()
        working_day = serializers.ChoiceField(
            choices=RosterUserSchedule.WorkingDay.labels
        )
        shift = serializers.ChoiceField(choices=RosterUserSchedule.Shift.labels)
        start_time = serializers.TimeField()
        end_time = serializers.TimeField()

        def validate_working_day(self, value):
            for choice, label in RosterUserSchedule.WorkingDay.choices:
                if label == value:
                    return choice

        def validate_shift(self, value):
            for choice, label in RosterUserSchedule.Shift.choices:
                if label == value:
                    return choice

    class OutputSerializer(RosterUserScheduleSerializer):
        class RosterOutputSerializer(RosterSerializer):
            class Meta:
                model = Roster
                fields = ("id", "title")

        class UserOutputSerializer(UserSerializer):
            full_name = serializers.CharField()

            class Meta:
                fields = ("id", "full_name")
                model = User

        roster = RosterOutputSerializer()
        user = UserOutputSerializer()

        class Meta:
            fields = (
                "id",
                "roster",
                "user",
                "shift",
                "working_day",
                "start_time",
                "end_time",
            )
            model = RosterUserSchedule

    def put(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

        try:
            roster_user_schedule = RosterUserSchedule.objects.get(
                date_deleted__isnull=True,
                id=kwargs["pk"],
                roster_id__in=RosterManager.objects.filter(
                    date_deleted__isnull=True, manager=request.user
                ).values_list("roster_id", flat=True),
            )
        except RosterUserSchedule.DoesNotExist:
            return CustomResponse(
                errors=OBJECT_NOT_FOUND.format(object="Roster user schedule"),
                status=HTTP_404_NOT_FOUND,
            )

        # Soft deleting old roster user schedule and creating new for given user
        if (
            validated_data.get("user")
            and roster_user_schedule.user_id != validated_data["user"]
        ):
            try:
                with transaction.atomic():
                    # Deleting old roster user schedule
                    success, message = delete_roster_user_schedule(
                        roster_user_schedule=roster_user_schedule,
                        updated_by=request.user,
                    )
                    if not success:
                        raise ValidationError(message)

                    # Creating new roster user schedule
                    success, new_roster_user_schedules = (
                        bulk_create_roster_user_schedules(
                            roster=roster_user_schedule.roster,
                            data=[
                                {
                                    "user": validated_data["user"],
                                    "working_day": validated_data.get(
                                        "working_day", roster_user_schedule.working_day
                                    ),
                                    "shift": validated_data.get(
                                        "shift", roster_user_schedule.shift
                                    ),
                                    "start_time": validated_data.get(
                                        "start_time", roster_user_schedule.start_time
                                    ),
                                    "end_time": validated_data.get(
                                        "end_time", roster_user_schedule.end_time
                                    ),
                                }
                            ],
                        )
                    )
                    if not success:
                        raise ValidationError(new_roster_user_schedules)

                    roster_user_schedule = new_roster_user_schedules[0]

            except ValidationError as error:
                return CustomResponse(errors=str(error), status=HTTP_400_BAD_REQUEST)

        else:
            validated_data.pop("user", None)
            success, roster_user_schedule = update_roster_user_schedule(
                roster_user_schedule=roster_user_schedule,
                **validated_data,
                updated_by=request.user
            )
            if not success:
                return CustomResponse(
                    errors=roster_user_schedule, status=HTTP_400_BAD_REQUEST
                )

        return CustomResponse(
            data=self.OutputSerializer(instance=roster_user_schedule).data,
            status=HTTP_200_OK,
        )


class ListRosterUserScheduleAPI(APIView):
    """
    This API is used to list the roster user schedule for staff member to see their assigned shifts
    Response codes: 200, 400, 404
    """

    permission_classes = (IsStaffMember,)

    class OutputSerializer(RosterUserScheduleSerializer):
        class RosterOutputSerializer(RosterSerializer):
            class Meta:
                model = Roster
                fields = ("id", "title")

        roster = RosterOutputSerializer()

        class Meta:
            fields = ("id", "roster", "shift", "working_day", "start_time", "end_time")
            model = RosterUserSchedule

    def get(self, request, *args, **kwargs):
        roster_user_schedules = RosterUserSchedule.objects.filter(
            date_deleted__isnull=True, user=request.user
        ).select_related("roster")

        return CustomResponse(
            data=self.OutputSerializer(instance=roster_user_schedules, many=True).data,
            status=HTTP_200_OK,
        )
