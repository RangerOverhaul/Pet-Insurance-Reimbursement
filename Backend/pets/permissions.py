from rest_framework import permissions
from users.models import User


class IsOwnerOrSupportOrAdmin(permissions.BasePermission):
    """
    - CUSTOMER: can only access their own pets
    - SUPPORT / ADMIN: can access all pets
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in [User.Role.SUPPORT, User.Role.ADMIN]:
            return True
        return obj.owner == request.user