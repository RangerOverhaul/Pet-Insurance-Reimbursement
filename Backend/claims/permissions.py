from rest_framework import permissions
from users.models import User


class IsClaimOwnerOrStaff(permissions.BasePermission):
    """CUSTOMER sees only their own claims. SUPPORT/ADMIN sees all."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.SUPPORT, User.Role.ADMIN]:
            return True
        return obj.owner == request.user


class IsSupportOrAdmin(permissions.BasePermission):
    """Only SUPPORT or ADMIN can perform the action."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.SUPPORT, User.Role.ADMIN
        ]