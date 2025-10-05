from __future__ import annotations
from typing import Any
from django.contrib.auth import login, logout
from django.contrib.auth.models import update_last_login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    BasicAuthSerializer, SessionLoginSerializer
)
from .throttles import IPBurstThrottle, IPSustainedThrottle

RATE_LIMIT_HEADERS = {
    "X-RateLimit-Policy": "burst=20/min, sustained=200/day"
}

class SecuredAPIView(APIView):
    throttle_classes = [IPBurstThrottle, IPSustainedThrottle]

@extend_schema(
    request=BasicAuthSerializer,
    responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}},
    tags=["Auth"],
    examples=[OpenApiExample("Basic auth", value={"username": "admin", "password": "pass"})],
)
class BasicAuthView(SecuredAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = BasicAuthSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        update_last_login(None, user)
        return Response({"status": "ok"}, headers=RATE_LIMIT_HEADERS)

@extend_schema(
    request=SessionLoginSerializer,
    responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}},
    tags=["Auth"],
)
class SessionLoginView(SecuredAPIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        ser = SessionLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        from django.contrib.auth import authenticate
        user = authenticate(username=ser.validated_data["username"], password=ser.validated_data["password"])
        if not user:
            return Response({"detail": "Invalid credentials."}, status=400)
        login(request, user)
        update_last_login(None, user)
        return Response({"status": "logged_in"}, headers=RATE_LIMIT_HEADERS)

@extend_schema(responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}, tags=["Auth"])
class SessionLogoutView(SecuredAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"status": "logged_out"}, headers=RATE_LIMIT_HEADERS)

@extend_schema(responses={200: {"type": "object", "properties": {"methods": {"type": "array", "items": {"type": "string"}}}}}, tags=["Auth"])
class AuthMethodsView(SecuredAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "methods": ["basic", "session", "jwt"],
            "mfa_ready": True
        }, headers=RATE_LIMIT_HEADERS)

# Re-export SimpleJWT views so they appear in docs under /api/auth/jwt/*
class JWTTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

class JWTTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

class JWTTokenVerifyView(TokenVerifyView):
    permission_classes = [permissions.AllowAny]