from __future__ import annotations
from typing import Optional
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    actor_ip = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=10)
    event = models.CharField(max_length=128)  # e.g. AUTH_LOGIN, PRIVACY_EXPORT
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "created_at"]), models.Index(fields=["path"])]

class Consent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="consent")
    marketing = models.BooleanField(default=False)
    data_processing = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

class GovernmentAccessRequest(models.Model):
    requester_email = models.EmailField()
    reason = models.TextField()
    status = models.CharField(max_length=24, default="pending")  # pending|approved|denied
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PermissionAuditLog(models.Model):
    admin = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    target = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    action = models.CharField(max_length=64)  # ASSIGN_ROLE|CREATE_ROLE|REMOVE_ROLE
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
