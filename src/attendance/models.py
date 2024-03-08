"""
This file contains all the models for attendance module
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now

from rosters.models import RosterUserSchedule
from utils.files import FILE_STORAGE, RenameFile, ValidateFileSize
from utils.models import BaseModel


class Attendance(BaseModel):
    """
    This model is used to store attendance of a user for a roster item
    """

    MAX_FILE_SIZE_ALLOWED = 5  # MB
    EXTENSIONS_ALLOWED = ("jpeg", "png", "jpg")

    roster_user_schedule = models.ForeignKey(
        RosterUserSchedule, on_delete=models.PROTECT
    )
    image = models.ImageField(
        storage=FILE_STORAGE,
        upload_to=RenameFile(
            "files/attendance/{instance.roster_user_schedule.user_id}/{instance.date_created}.{extension}"
        ),
        validators=[
            ValidateFileSize(max_file_size=MAX_FILE_SIZE_ALLOWED),
            FileExtensionValidator(allowed_extensions=EXTENSIONS_ALLOWED),
        ],
        null=True,
        blank=True,
    )
    attendance_time = models.DateTimeField(default=now)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"
