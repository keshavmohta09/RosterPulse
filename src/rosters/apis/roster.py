"""
This file contains all the APIs related to roster model
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from rosters.constants import START_TIME_MUST_BE_BEFORE_THAN_END_TIME
from rosters.models import Roster, RosterManager, RosterUserSchedule
from rosters.serializers import RosterSerializer, RosterUserScheduleSerializer
from rosters.services import (
    bulk_create_roster_user_schedules,
    create_roster,
    create_roster_manager,
)
from users.models import User
from users.permissions import IsManager
from users.serializers import UserSerializer
from utils.response import CustomResponse


class CreateRosterAPI(APIView):
    """
    This API is used to create the roster
    Response codes: 201, 400
    """

    permission_classes = (IsManager,)

    class InputSerializer(serializers.Serializer):
        class RosterUserScheduleInputSerializer(serializers.Serializer):
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

            def validate(self, attrs):
                if attrs["start_time"] >= attrs["end_time"]:
                    raise serializers.ValidationError(
                        {"start_time": START_TIME_MUST_BE_BEFORE_THAN_END_TIME}
                    )

                return super().validate(attrs)

        title = serializers.CharField(max_length=256, required=False)
        roster_user_schedules = RosterUserScheduleInputSerializer(many=True)

    class OutputSerializer(RosterSerializer):

        class RosterUserScheduleOutputSerializer(RosterUserScheduleSerializer):

            class UserOutputSerializer(UserSerializer):
                full_name = serializers.CharField()

                class Meta:
                    fields = ("id", "full_name")
                    model = User

            user = UserOutputSerializer()

            class Meta:
                fields = (
                    "id",
                    "user",
                    "shift",
                    "working_day",
                    "start_time",
                    "end_time",
                )
                model = RosterUserSchedule

        roster_user_schedules = RosterUserScheduleOutputSerializer(many=True)

        class Meta:
            fields = ("id", "title", "is_active", "roster_user_schedules")
            model = Roster

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            with transaction.atomic():
                success, roster = create_roster(
                    title=validated_data["title"],
                    is_active=True,
                    created_by=request.user,
                )
                if not success:
                    raise ValidationError(message=roster)

                success, roster_manager = create_roster_manager(
                    roster=roster,
                    manager=request.user,
                    created_by=request.user,
                )
                if not success:
                    raise ValidationError(message=roster_manager)

                if validated_data["roster_user_schedules"]:
                    success, roster_user_schedules = bulk_create_roster_user_schedules(
                        roster=roster,
                        data=validated_data["roster_user_schedules"],
                        created_by=request.user,
                    )
                    if not success:
                        raise ValidationError(message=roster_user_schedules)
        except ValidationError as error:
            return CustomResponse(errors=str(error), status=HTTP_400_BAD_REQUEST)

        roster.roster_user_schedules = roster_user_schedules

        return CustomResponse(
            data=self.OutputSerializer(instance=roster).data,
            status=HTTP_201_CREATED,
        )


class ListRosterAPI(APIView):
    """
    This API is used to list all the rosters of a manager
    Response codes: 200, 400
    """

    permission_classes = (IsManager,)

    class OutputSerializer(RosterSerializer):

        class RosterUserScheduleOutputSerializer(RosterUserScheduleSerializer):

            class UserOutputSerializer(UserSerializer):
                full_name = serializers.CharField()

                class Meta:
                    fields = ("id", "full_name")
                    model = User

            user = UserOutputSerializer()

            class Meta:
                fields = (
                    "id",
                    "user",
                    "shift",
                    "working_day",
                    "start_time",
                    "end_time",
                )
                model = RosterUserSchedule

        roster_user_schedules = RosterUserScheduleOutputSerializer(many=True)

        class Meta:
            fields = ("id", "title", "is_active", "roster_user_schedules")
            model = Roster

    def get(self, request, *args, **kwargs):
        rosters = Roster.objects.filter(
            date_deleted__isnull=True,
            id__in=RosterManager.objects.filter(manager=request.user).values_list(
                "roster_id", flat=True
            ),
        ).prefetch_related(
            Prefetch(
                "rosteruserschedule_set",
                queryset=RosterUserSchedule.objects.filter(date_deleted__isnull=True),
                to_attr="roster_user_schedules",
            )
        )

        return CustomResponse(
            data=self.OutputSerializer(instance=rosters, many=True).data,
            status=HTTP_200_OK,
        )
