"""
This file contains all the create services for attendance module.
"""

from typing import Tuple, Union

from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.db.models import Q
from django.utils.timezone import now

from attendance.models import Attendance
from rosters.models import RosterUserSchedule
from users.models import User


def create_attendance(
    roster_user_schedule: Union[int, RosterUserSchedule],
    image: ImageFile,
    created_by: User = None,
) -> Tuple[bool, Union[str, Attendance]]:
    """
    This service is used to create attendance
    """
    attendance = Attendance(
        roster_user_schedule_id=(
            roster_user_schedule.id
            if isinstance(roster_user_schedule, RosterUserSchedule)
            else roster_user_schedule
        ),
        image=image,
        created_by=created_by,
    )

    try:
        attendance.save()
    except ValidationError as error:
        return False, str(error)

    return True, attendance
