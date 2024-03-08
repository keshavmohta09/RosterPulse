"""
This file contains all the models for rosters module
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from rosters.constants import (
    START_TIME_MUST_BE_BEFORE_THAN_END_TIME,
    USER_SHOULD_HAVE_MANAGER_ROLE_TO_CREATE_ROSTER_MANAGER,
    USER_SHOULD_HAVE_STAFF_MEMBER_ROLE_TO_CREATE_ROSTER_USER_SCHEDULE,
)
from users.models import User, UserRole
from utils.constants import DATE_CANNOT_BE_IN_PAST
from utils.models import BaseModel


class Roster(BaseModel):
    """
    This model is used to store roster_user_schedule group for multiple roster user schedules
    """

    title = models.CharField(max_length=256)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Roster"
        verbose_name_plural = "Rosters"


class RosterUserSchedule(BaseModel):
    """
    This model is used to store roster_user_schedules for a roster user schedule group
    """

    class WorkingDay(models.IntegerChoices):
        MONDAY = 1
        TUESDAY = 2
        WEDNESDAY = 3
        THURSDAY = 4
        FRIDAY = 5
        SATURDAY = 6
        SUNDAY = 7

    class Shift(models.IntegerChoices):
        MORNING_SHIFT = 1
        EVENING_SHIFT = 2

    roster = models.ForeignKey(Roster, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    working_day = models.PositiveSmallIntegerField(choices=WorkingDay.choices)
    shift = models.PositiveSmallIntegerField(choices=Shift.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.roster.title}-{self.user.email}"

    class Meta:
        verbose_name = "Roster User Schedule"
        verbose_name_plural = "Roster User Schedules"
        # Partial indexing when date deleted is not null
        constraints = [
            models.UniqueConstraint(
                fields=["roster", "user", "working_day", "shift"],
                name="roster_user_working_day_shift_unique_constraint",
                condition=models.Q(date_deleted__isnull=True),
            )
        ]

    def validate_user(self):
        """
        This function is used to validate that user should be staff member.
        """
        if not UserRole.objects.filter(
            user_id=self.user_id,
            role=UserRole.Role.STAFF_MEMBER,
            date_deleted__isnull=True,
        ).exists():
            raise ValidationError(
                USER_SHOULD_HAVE_STAFF_MEMBER_ROLE_TO_CREATE_ROSTER_USER_SCHEDULE
            )

    def validate_date_fields(self):
        if self.end_time <= self.start_time:
            raise ValidationError(START_TIME_MUST_BE_BEFORE_THAN_END_TIME)

    def clean(self) -> None:
        self.validate_date_fields()
        return super().clean()

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_user()
        return super().full_clean(*args, **kwargs)


class RosterManager(BaseModel):
    """
    This model is used to store roster and user having manager role mapping
    """

    roster = models.ForeignKey(Roster, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.roster} - {self.manager}"

    class Meta:
        verbose_name = "Roster Manager"
        verbose_name_plural = "Roster Managers"
        constraints = [
            models.UniqueConstraint(
                fields=["roster", "manager"],
                name="roster_manager_unique_constraint",
            )
        ]

    def validate_manager(self):
        if not UserRole.objects.filter(
            user_id=self.manager_id,
            role=UserRole.Role.MANAGER,
            date_deleted__isnull=True,
        ).exists():
            raise ValidationError(
                USER_SHOULD_HAVE_MANAGER_ROLE_TO_CREATE_ROSTER_MANAGER
            )

    def full_clean(self, *args, **kwargs) -> None:
        self.validate_manager()
        return super().full_clean(*args, **kwargs)
