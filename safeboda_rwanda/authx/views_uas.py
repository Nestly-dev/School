from __future__ import annotations
from typing import Any
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.crypto import get_random_string
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    UASRegisterSerializer, UASVerifyCodeSerializer, UASAccountStatusSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()

VERIFY_TTL = 10 * 60  # 10 minutes

def _code_key(target: str, value: str) -> str:
    return f"uas_code::{target}::{value}"

@extend_schema(request=UASRegisterSerializer, responses={201: {"type": "object"}}, tags=["UAS"])
class UASRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = UASRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        phone = ser.validated_data["phone"]
        password = ser.validated_data["password"]

        user, created = User.objects.get_or_create(email=email, defaults={"username": email})
        if created:
            user.set_password(password)
            user.save()

        # simulate sending codes via cache
        phone_code = get_random_string(6, "0123456789")
        email_code = get_random_string(6, "0123456789")
        cache.set(_code_key("phone", phone), phone_code, VERIFY_TTL)
        cache.set(_code_key("email", email), email_code, VERIFY_TTL)

        return Response({
            "status": "registered",
            "verification": {"phone": "SENT", "email": "SENT"},
            "hints": {"phone_code": phone_code, "email_code": email_code}  # show in dev only
        }, status=201)

@extend_schema(request=UASVerifyCodeSerializer, responses={200: {"type": "object"}}, tags=["UAS"])
class UASVerifyPhoneView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        s = UASVerifyCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if s.validated_data["target"] != "phone":
            return Response({"detail": "target must be 'phone'."}, status=400)
        ok = cache.get(_code_key("phone", s.validated_data["value"])) == s.validated_data["code"]
        return Response({"verified": bool(ok)})

@extend_schema(request=UASVerifyCodeSerializer, responses={200: {"type": "object"}}, tags=["UAS"])
class UASVerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        s = UASVerifyCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if s.validated_data["target"] != "email":
            return Response({"detail": "target must be 'email'."}, status=400)
        ok = cache.get(_code_key("email", s.validated_data["value"])) == s.validated_data["code"]
        return Response({"verified": bool(ok)})

@extend_schema(request=PasswordResetRequestSerializer, responses={200: {"type": "object"}}, tags=["UAS"])
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        s = PasswordResetRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        # Simulate: generate token & cache. (In prod use Email + default tokens)
        token = get_random_string(24)
        cache.set(f"pwd::{s.validated_data['email'].lower()}", token, 15 * 60)
        return Response({"status": "SENT", "dev_token": token})

@extend_schema(request=PasswordResetConfirmSerializer, responses={200: {"type": "object"}}, tags=["UAS"])
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        s = PasswordResetConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        # For demo we accept uid=email
        email = s.validated_data["uid"].lower()
        token_ok = cache.get(f"pwd::{email}") == s.validated_data["token"]
        if not token_ok:
            return Response({"detail": "Invalid token."}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Unknown user."}, status=404)
        user.set_password(s.validated_data["new_password"])
        user.save()
        cache.delete(f"pwd::{email}")
        return Response({"status": "PASSWORD_UPDATED"})

@extend_schema(responses={200: UASAccountStatusSerializer}, tags=["UAS"])
class UASAccountStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # For demo, infer from cache ticks or simple defaults.
        email = request.user.email or ""
        phone_verified = bool(cache.get(f"ua_phone_ok::{email}"))  # not set here, but left for future
        email_verified = False  # you can switch to True once verified flow updates it in DB/cache
        return Response({
            "email_verified": email_verified,
            "phone_verified": phone_verified,
            "profile_complete": True,
        })
