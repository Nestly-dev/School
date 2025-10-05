from rest_framework.permissions import BasePermission

def _role(user):
    val = getattr(user, "role", None)
    if isinstance(val, str):
        return val.upper()
    if getattr(user, "is_driver", False):
        return "DRIVER"
    return "RIDER"

class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _role(request.user) == "DRIVER"

class IsRider(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and _role(request.user) != "DRIVER"
