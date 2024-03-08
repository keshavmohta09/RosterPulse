"""
This file contains all the APIs related to attendance model
"""

from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from attendance.services import create_attendance
from rosters.serializers import RosterUserScheduleSerializer
from users.permissions import IsStaffMember
from utils.files import ValidateFileSize
from utils.response import CustomResponse


class CreateAttendanceAPI(APIView):
    """
    This API is used to create attendance for a staff member
    Response codes: 201, 400
    """

    permission_classes = (IsStaffMember,)

    class InputSerializer(serializers.Serializer):
        roster_user_schedule = serializers.IntegerField()
        image = serializers.ImageField(
            validators=[
                ValidateFileSize(max_file_size=Attendance.MAX_FILE_SIZE_ALLOWED),
                FileExtensionValidator(
                    allowed_extensions=Attendance.EXTENSIONS_ALLOWED
                ),
            ]
        )

    class OutputSerializer(AttendanceSerializer):
        roster_user_schedule = RosterUserScheduleSerializer()

        class Meta:
            model = Attendance
            fields = ("id", "roster_user_schedule", "image")

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

        success, attendance = create_attendance(**validated_data)
        if not success:
            return CustomResponse(errors=attendance, status=HTTP_400_BAD_REQUEST)

        return CustomResponse(
            data=self.OutputSerializer(instance=attendance).data,
            status=HTTP_201_CREATED,
        )
