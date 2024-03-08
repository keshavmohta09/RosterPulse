"""
This file contains all the update services for rosters module
"""

from datetime import time
from typing import Optional, Tuple, Union

from django.core.exceptions import ValidationError
from django.utils.functional import empty

from rosters.models import Roster, RosterUserSchedule
from users.models import User
from utils.constants import (
    AT_LEAST_ONE_FIELD_MUST_BE_UPDATED,
    VARIABLE_MUST_BE_INSTANCE,
)


def update_roster_user_schedule(
    *,
    roster_user_schedule: RosterUserSchedule,
    roster: Union[Roster, int] = empty,
    working_day: int = empty,
    shift: int = empty,
    start_time: time = empty,
    end_time: time = empty,
    updated_by: Optional[User] = None,
) -> Tuple[bool, Union[RosterUserSchedule, str]]:
    """
    This service is used to update roster user schedule
    """
    assert isinstance(
        roster_user_schedule, RosterUserSchedule
    ), VARIABLE_MUST_BE_INSTANCE.format(
        variable="roster_user_schedule", model="RosterUserSchedule"
    )

    fields = {
        "roster_id": roster.id if isinstance(roster, Roster) else roster,
        "working_day": working_day,
        "shift": shift,
        "start_time": start_time,
        "end_time": end_time,
    }

    update_fields = []
    for field, value in fields.items():
        if value != empty:
            setattr(roster_user_schedule, field, value)
            update_fields.append(field)

    if not update_fields:
        return False, AT_LEAST_ONE_FIELD_MUST_BE_UPDATED

    roster_user_schedule.updated_by = updated_by
    update_fields.extend(["date_updated", "updated_by"])

    try:
        roster_user_schedule.save(update_fields=update_fields)
    except ValidationError as error:
        return False, str(error=error)

    return True, roster_user_schedule
