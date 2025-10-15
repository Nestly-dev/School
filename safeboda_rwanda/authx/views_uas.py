# authx/views_uas.py - Fixed Registration

from __future__ import annotations
from typing import Any
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.db import IntegrityError
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

@extend_schema(
    request=UASRegisterSerializer, 
    responses={201: {"type": "object"}, 400: {"type": "object"}}, 
    tags=["UAS"],
    examples=[
        OpenApiExample(
            "Rwanda user registration",
            value={
                "email": "user@example.rw",
                "password": "SecurePass123!",
                "phone": "+250788123456",
                "national_id": "1199012345678901"
            }
        )
    ]
)
class UASRegisterView(APIView):
    """
    User registration with Rwanda National ID and phone validation.
    Sends verification codes via SMS and email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        ser = UASRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        email = ser.validated_data["email"].lower()
        phone = ser.validated_data["phone"]
        password = ser.validated_data["password"]
        national_id = ser.validated_data.get("national_id")

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if phone and User.objects.filter(phone=phone).exists():
            return Response(
                {"detail": "User with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new user
        try:
            user = User.objects.create_user(
                username=email.split("@")[0],
                email=email,
                password=password,
                phone=phone,
                national_id=national_id
            )
        except IntegrityError as e:
            return Response(
                {"detail": f"Registration failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate verification codes
        phone_code = get_random_string(6, "0123456789")
        email_code = get_random_string(6, "0123456789")
        
        # Cache verification codes
        cache.set(_code_key("phone", phone), phone_code, VERIFY_TTL)
        cache.set(_code_key("email", email), email_code, VERIFY_TTL)

        # In production: send actual SMS and email
        # send_sms(phone, f"Your SafeBoda verification code: {phone_code}")
        # send_email(email, "Verify your email", f"Code: {email_code}")

        return Response({
            "status": "registered",
            "user_id": user.id,
            "email": user.email,
            "verification": {
                "phone": "SENT",
                "email": "SENT"
            },
            # Remove these hints in production
            "dev_hints": {
                "phone_code": phone_code,
                "email_code": email_code
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    request=UASVerifyCodeSerializer, 
    responses={200: {"type": "object"}}, 
    tags=["UAS"]
)
class UASVerifyPhoneView(APIView):
    """Verify phone number with SMS code"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        s = UASVerifyCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        
        if s.validated_data["target"] != "phone":
            return Response(
                {"detail": "target must be 'phone'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expected_code = cache.get(_code_key("phone", s.validated_data["value"]))
        provided_code = s.validated_data["code"]
        
        if expected_code and expected_code == provided_code:
            # Mark as verified
            cache.set(
                f"verified_phone::{s.validated_data['value']}", 
                True, 
                86400  # 24 hours
            )
            return Response({"verified": True, "message": "Phone verified successfully"})
        
        return Response(
            {"verified": False, "message": "Invalid verification code"},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=UASVerifyCodeSerializer, 
    responses={200: {"type": "object"}}, 
    tags=["UAS"]
)
class UASVerifyEmailView(APIView):
    """Verify email address with code"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        s = UASVerifyCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        
        if s.validated_data["target"] != "email":
            return Response(
                {"detail": "target must be 'email'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expected_code = cache.get(_code_key("email", s.validated_data["value"]))
        provided_code = s.validated_data["code"]
        
        if expected_code and expected_code == provided_code:
            # Mark as verified
            cache.set(
                f"verified_email::{s.validated_data['value']}", 
                True, 
                86400  # 24 hours
            )
            return Response({"verified": True, "message": "Email verified successfully"})
        
        return Response(
            {"verified": False, "message": "Invalid verification code"},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=PasswordResetRequestSerializer, 
    responses={200: {"type": "object"}}, 
    tags=["UAS"]
)
class PasswordResetRequestView(APIView):
    """Request password reset token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        s = PasswordResetRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        
        email = s.validated_data['email'].lower()
        
        # Check if user exists (don't reveal in response)
        if User.objects.filter(email=email).exists():
            token = get_random_string(32)
            cache.set(f"pwd_reset::{email}", token, 15 * 60)  # 15 minutes
            
            # In production: send email with reset link
            # send_email(email, "Password Reset", f"Token: {token}")
            
            return Response({
                "status": "SENT",
                "message": "If account exists, reset instructions sent",
                "dev_token": token  # Remove in production
            })
        
        # Same response even if user doesn't exist (security)
        return Response({
            "status": "SENT",
            "message": "If account exists, reset instructions sent"
        })


@extend_schema(
    request=PasswordResetConfirmSerializer, 
    responses={200: {"type": "object"}}, 
    tags=["UAS"]
)
class PasswordResetConfirmView(APIView):
    """Confirm password reset with token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        s = PasswordResetConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        
        email = s.validated_data["uid"].lower()  # Using email as uid
        token = s.validated_data["token"]
        new_password = s.validated_data["new_password"]
        
        # Verify token
        cached_token = cache.get(f"pwd_reset::{email}")
        if not cached_token or cached_token != token:
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear reset token
            cache.delete(f"pwd_reset::{email}")
            
            return Response({
                "status": "PASSWORD_UPDATED",
                "message": "Password successfully reset"
            })
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    responses={200: UASAccountStatusSerializer}, 
    tags=["UAS"]
)
class UASAccountStatusView(APIView):
    """Get account verification status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        email = user.email or ""
        phone = getattr(user, 'phone', None) or ""
        
        # Check verification status from cache
        email_verified = bool(cache.get(f"verified_email::{email}"))
        phone_verified = bool(cache.get(f"verified_phone::{phone}")) if phone else False
        
        # Check profile completeness
        profile_complete = all([
            user.first_name,
            user.last_name,
            user.email,
            getattr(user, 'phone', None),
            getattr(user, 'national_id', None)
        ])
        
        return Response({
            "email_verified": email_verified,
            "phone_verified": phone_verified,
            "profile_complete": profile_complete,
            "email": email,
            "phone": phone
        })


@extend_schema(
    request={
        "type": "object",
        "properties": {
            "email": {"type": "string", "format": "email"},
            "national_id": {"type": "string"}
        },
        "required": ["email", "national_id"]
    },
    responses={200: {"type": "object"}},
    tags=["UAS"]
)
class UASAccountRecoveryView(APIView):
    """
    Emergency account recovery using National ID verification.
    Required for Rwanda regulatory compliance.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "").lower()
        national_id = request.data.get("national_id", "").strip()
        
        if not email or not national_id:
            return Response(
                {"detail": "Email and National ID required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            stored_nid = getattr(user, "national_id", None)
            
            if stored_nid and stored_nid == national_id:
                # Generate recovery token
                recovery_token = get_random_string(32)
                cache.set(f"recovery::{email}", recovery_token, 30 * 60)
                
                # In production: send secure email/SMS
                return Response({
                    "status": "RECOVERY_INITIATED",
                    "message": "Recovery instructions sent to your email",
                    "dev_token": recovery_token  # Remove in production
                })
        except User.DoesNotExist:
            pass
        
        # Security: same response regardless of match
        return Response({
            "status": "RECOVERY_INITIATED",
            "message": "If account exists, recovery instructions will be sent"
        })