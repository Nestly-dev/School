from __future__ import annotations
from typing import Any, Optional
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()

class BasicAuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data

class SessionLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

class ConsentSerializer(serializers.Serializer):
    marketing = serializers.BooleanField(required=False)
    data_processing = serializers.BooleanField(required=False)

class GovernmentAccessRequestSerializer(serializers.Serializer):
    requester_email = serializers.EmailField()
    reason = serializers.CharField()

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.CharField()

class CreateRoleSerializer(serializers.Serializer):
    name = serializers.CharField()
    permissions = serializers.ListField(child=serializers.CharField(), required=False)

# UAS
class UASRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField()
    national_id = serializers.CharField()
    def validate_password(self, value):
        validate_password(value)
        return value

class UASVerifyCodeSerializer(serializers.Serializer):
    target = serializers.CharField()  # "phone"|"email"
    value = serializers.CharField()
    code = serializers.CharField()

class UASAccountStatusSerializer(serializers.Serializer):
    email_verified = serializers.BooleanField()
    phone_verified = serializers.BooleanField()
    profile_complete = serializers.BooleanField()
