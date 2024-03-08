"""
This file contains all the create services for rosters module.
"""

from datetime import time
from typing import List, Optional, Tuple, TypedDict, Union

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rosters.models import Roster, RosterManager, RosterUserSchedule
from users.constants import ALL_USERS_MUST_BE_STAFF_MEMBERS
from users.models import User, UserRole


class RosterUserScheduleData(TypedDict):
    user: Union[int, User]
    working_day: int
    shift: int
    start_time: time
    end_time: time


def create_roster(
    title: str, is_active: bool = False, created_by: Optional[User] = None
) -> Tuple[bool, Union[str, List[Roster]]]:
    """
    This service is used to create roster
    """
    roster = Roster(title=title, is_active=is_active, created_by=created_by)

    try:
        roster.save()
    except ValidationError as error:
        return False, str(error)

    return True, roster


def create_roster_manager(
    roster: Union[Roster, int],
    manager: Union[User, int],
    created_by: Optional[User] = None,
) -> Tuple[bool, Union[str, RosterManager]]:
    """
    This service is used to create roster user
    """

    roster_manager = RosterManager(
        roster_id=(roster.id if isinstance(roster, Roster) else roster),
        manager_id=manager.id if isinstance(manager, User) else manager,
        created_by=created_by,
    )

    try:
        roster_manager.save()
    except ValidationError as error:
        return False, str(error)

    return True, roster_manager


def bulk_create_roster_user_schedules(
    roster: Union[int, Roster],
    data: List[RosterUserScheduleData],
    created_by: Optional[User] = None,
) -> Tuple[bool, Union[str, List[RosterUserSchedule]]]:
    """
    This service is used to create multiple roster user schedules for a roster
    """
    if isinstance(roster, Roster):
        roster = roster.id

    all_user_ids = [
        (datum["user"].id if isinstance(datum["user"], User) else datum["user"])
        for datum in data
    ]
    if (
        len(all_user_ids)
        != UserRole.objects.filter(
            user_id__in=all_user_ids,
            role=UserRole.Role.STAFF_MEMBER,
            date_deleted__isnull=True,
        ).count()
    ):
        return False, ALL_USERS_MUST_BE_STAFF_MEMBERS

    roster_user_schedules = []
    try:
        for datum in data:
            if isinstance(datum["user"], User):
                datum["user"] = datum["user"].id

            roster_user_schedule = RosterUserSchedule(
                roster_id=roster,
                user_id=datum["user"],
                shift=datum["shift"],
                working_day=datum["working_day"],
                start_time=datum["start_time"],
                end_time=datum["end_time"],
                created_by=created_by,
            )

            roster_user_schedule.clean_fields(exclude=["roster", "user", "created_by"])
            roster_user_schedule.clean()
            roster_user_schedules.append(roster_user_schedule)

        roster_user_schedules = RosterUserSchedule.objects.bulk_create(
            objs=roster_user_schedules
        )
    except ValidationError as error:
        return False, str(error)
    except IntegrityError as error:
        return False, str(error)

    return True, roster_user_schedules
