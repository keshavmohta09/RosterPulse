"""
This file contains all the utils related to models
"""

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class BaseModel(models.Model):
    """
    This abstract model is used to add log fields in other models.
    Contains the created_by, updated_by, date_created, date_updated fields
    """

    # List of Log Fields
    LOG_FIELDS = (
        "date_created",
        "date_updated",
        "date_deleted",
        "created_by",
        "updated_by",
    )

    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created_by",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )

    date_created = models.DateTimeField(default=now)
    date_updated = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        skip_clean = kwargs.pop("skip_clean", False)
        if not skip_clean:
            self.full_clean(exclude=kwargs.pop("exclude_clean", None))
        return super().save(*args, **kwargs)
