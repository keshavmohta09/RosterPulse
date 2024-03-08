"""
This file contains all the delete services for rosters module.
"""

from typing import Optional, Tuple

from django.utils.timezone import now

from rosters.models import RosterUserSchedule
from users.models import User
from utils.constants import OBJECT_DELETED_SUCCESSFULLY, VARIABLE_MUST_BE_INSTANCE


def delete_roster_user_schedule(
    roster_user_schedule: RosterUserSchedule, updated_by: Optional[User] = None
) -> Tuple[bool, str]:
    """
    This service is used to soft delete roster user schedule by populating date deleted field value
    """
    assert isinstance(
        roster_user_schedule, RosterUserSchedule
    ), VARIABLE_MUST_BE_INSTANCE.format(
        variable="roster_user_schedule", model="RosterUserSchedule"
    )

    roster_user_schedule.date_deleted = now()
    roster_user_schedule.updated_by = updated_by

    roster_user_schedule.save(update_fields=["date_deleted", "updated_by"])
    return True, OBJECT_DELETED_SUCCESSFULLY
