from __future__ import annotations
from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .serializers import AssignRoleSerializer, CreateRoleSerializer
from .models import GovernmentAccessRequest, PermissionAuditLog

User = get_user_model()

ROLE_ORDER = ["passenger", "driver", "admin", "super_admin"]

def _ensure_roles():
    for name in ROLE_ORDER:
        Group.objects.get_or_create(name=name)

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.groups.filter(name="super_admin").exists()

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_staff or request.user.is_superuser or
                request.user.groups.filter(name__in=["admin", "super_admin"]).exists())

@extend_schema(tags=["RBAC"])
class RolesListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        _ensure_roles()
        return Response({"roles": list(Group.objects.values_list("name", flat=True))})

@extend_schema(tags=["RBAC"])
class AssignRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    def post(self, request, *args, **kwargs):
        s = AssignRoleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        _ensure_roles()
        try:
            target = User.objects.get(pk=s.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        try:
            role = Group.objects.get(name=s.validated_data["role"])
        except Group.DoesNotExist:
            return Response({"detail": "Role not found."}, status=404)
        target.groups.clear()
        target.groups.add(role)
        PermissionAuditLog.objects.create(admin=request.user, target=target, action="ASSIGN_ROLE",
                                          payload={"role": role.name})
        return Response({"status": "ASSIGNED", "user_id": target.id, "role": role.name})

@extend_schema(tags=["RBAC"])
class PermissionsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        groups = list(request.user.groups.values_list("name", flat=True))
        return Response({"roles": groups, "is_staff": request.user.is_staff, "is_superuser": request.user.is_superuser})

@extend_schema(tags=["RBAC"])
class AdminUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by("id")[:200]
        return Response([{"id": u.id, "email": u.email, "roles": list(u.groups.values_list("name", flat=True))} for u in users])

@extend_schema(tags=["RBAC"])
class GovernmentAccessRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    def post(self, request, *args, **kwargs):
        ser = GovernmentAccessRequest.objects.create(
            requester_email=request.data.get("requester_email", ""),
            reason=request.data.get("reason", ""),
        )
        return Response({"id": ser.id, "status": ser.status})

@extend_schema(tags=["RBAC"])
class PermissionAuditView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    def get(self, request, *args, **kwargs):
        logs = PermissionAuditLog.objects.order_by("-created_at")[:100]
        return Response([{"admin": l.admin_id, "target": l.target_id, "action": l.action, "when": l.created_at.isoformat(), "payload": l.payload} for l in logs])

@extend_schema(tags=["RBAC"])
class CreateRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    def post(self, request, *args, **kwargs):
        s = CreateRoleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        role, created = Group.objects.get_or_create(name=s.validated_data["name"])
        perms = s.validated_data.get("permissions") or []
        if perms:
            qs = Permission.objects.filter(codename__in=perms)
            role.permissions.set(qs)
        role.save()
        PermissionAuditLog.objects.create(admin=request.user, target=None, action="CREATE_ROLE",
                                          payload={"name": role.name, "perms": perms})
        return Response({"status": "CREATED", "role": role.name})
