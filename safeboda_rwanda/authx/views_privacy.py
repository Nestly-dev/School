from __future__ import annotations
from typing import Any
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import AuditLog, Consent

User = get_user_model()

RETENTION_TEXT = (
    "We retain essential account, transaction and audit data for 7 years or "
    "as required by RURA and applicable law. You may request deletion/anonymization "
    "for non-regulatory data."
)

@extend_schema(tags=["Privacy"])
class DataExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # Minimal example: export basic user fields + consent
        payload = {
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": getattr(user, "first_name", ""),
                "last_name": getattr(user, "last_name", ""),
            },
            "consent": {
                "marketing": getattr(getattr(user, "consent", None), "marketing", False),
                "data_processing": getattr(getattr(user, "consent", None), "data_processing", True),
            },
        }
        AuditLog.objects.create(user=user, path="/api/privacy/data-export/", method="GET", event="PRIVACY_EXPORT")
        return JsonResponse(payload)

@extend_schema(tags=["Privacy"])
class DataDeletionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        AuditLog.objects.create(user=request.user, path="/api/privacy/data-deletion/", method="DELETE", event="PRIVACY_DELETE_REQ")
        # In production, queue a GDPR-like deletion workflow
        return Response({"status": "REQUEST_RECEIVED"})

@extend_schema(tags=["Privacy"])
class AuditLogView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logs = (AuditLog.objects
                .filter(user=request.user)
                .order_by("-created_at")[:100])
        return Response([{
            "time": l.created_at.isoformat(),
            "path": l.path, "method": l.method, "event": l.event, "detail": l.detail
        } for l in logs])

@extend_schema(tags=["Privacy"])
class ConsentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        c, _ = Consent.objects.get_or_create(user=request.user)
        return Response({"marketing": c.marketing, "data_processing": c.data_processing})

    def post(self, request, *args, **kwargs):
        c, _ = Consent.objects.get_or_create(user=request.user)
        c.marketing = bool(request.data.get("marketing", c.marketing))
        c.data_processing = bool(request.data.get("data_processing", c.data_processing))
        c.save()
        AuditLog.objects.create(user=request.user, path="/api/privacy/consent/", method="POST", event="PRIVACY_CONSENT_UPDATE", detail=request.data)
        return Response({"status": "UPDATED", "marketing": c.marketing, "data_processing": c.data_processing})

@extend_schema(tags=["Privacy"])
class AnonymizeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Example: scramble non-regulatory fields (DO NOT remove IDs needed for audits)
        user = request.user
        if hasattr(user, "first_name"): user.first_name = "anon"
        if hasattr(user, "last_name"): user.last_name = "user"
        user.save(update_fields=[f for f in ["first_name", "last_name"] if hasattr(user, f)])
        AuditLog.objects.create(user=user, path="/api/privacy/anonymize/", method="POST", event="PRIVACY_ANON")
        return Response({"status": "ANONYMIZED"})

@extend_schema(tags=["Privacy"])
class RetentionPolicyView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"policy": RETENTION_TEXT})
