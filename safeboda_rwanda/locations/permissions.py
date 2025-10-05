from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.core.exceptions import FieldDoesNotExist


def user_is_driver(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    # If your custom User has user_type
    User = get_user_model()
    try:
        User._meta.get_field("user_type")
        if getattr(user, "user_type", None) == "driver":
            return True
    except FieldDoesNotExist:
        pass

    # Or use groups (case-insensitive)
    if user.groups.filter(name__iexact="driver").exists():
        return True

    return False


class IsDriverOrAdmin(BasePermission):
    """
    Drivers can update their own location; admins/staff can do anything.
    Read-only endpoints allow any authenticated user by default (tuned in views).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or user_is_driver(request.user))
        )
