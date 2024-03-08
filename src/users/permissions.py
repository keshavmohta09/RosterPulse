"""
This file contains all the permissions related to users module
"""

from rest_framework.permissions import IsAuthenticated

from users.models import UserRole


class IsManager(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.userrole_set.filter(role=UserRole.Role.MANAGER).exists()
        )


class IsStaffMember(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.userrole_set.filter(
                role=UserRole.Role.STAFF_MEMBER
            ).exists()
        )
