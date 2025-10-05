from __future__ import annotations

from typing import Any, Optional

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    Read-only lightweight user row for /api/users/ listing.
    NOTE: Fields like user_type may not exist on your model, so we expose them
    as computed fields to keep schema generation stable.
    """
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "user_type",  # computed (safe even if model has no such column)
        )
        read_only_fields = fields

    def get_user_type(self, obj: User) -> Optional[str]:
        # 1) If your model eventually gets a "user_type" field, use it
        if hasattr(obj, "user_type"):
            return getattr(obj, "user_type")  # type: ignore[attr-defined]

        # 2) Common project patterns:
        #    - a related profile with user_type
        profile = getattr(obj, "profile", None)
        if profile and hasattr(profile, "user_type"):
            return getattr(profile, "user_type")

        # 3) Heuristic: mark as "driver" if a driver_location relation exists
        if getattr(obj, "driver_location", None) is not None:
            return "driver"

        # 4) Fallback
        return "passenger"


class DriverListSerializer(serializers.ModelSerializer):
    """
    Read-only driver list row. Uses heuristics for rating & location if those
    live on related objects (e.g., driver_profile, driver_location).
    """
    user_type = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "rating",
            "location",
        )
        read_only_fields = fields

    def get_user_type(self, obj: User) -> str:
        # Prefer explicit model field if present
        if hasattr(obj, "user_type"):
            return getattr(obj, "user_type")  # type: ignore[attr-defined]
        return "driver"

    def get_rating(self, obj: User) -> Optional[float]:
        driver_profile = getattr(obj, "driver_profile", None)
        if driver_profile and hasattr(driver_profile, "rating"):
            return getattr(driver_profile, "rating")
        return None

    def get_location(self, obj: User) -> Optional[dict[str, float]]:
        dl = getattr(obj, "driver_location", None)
        if not dl:
            return None
        lat = getattr(dl, "lat", None)
        lng = getattr(dl, "lng", None)
        if lat is None or lng is None:
            return None
        return {"lat": float(lat), "lng": float(lng)}


class RegistrationSerializer(serializers.Serializer):
    """
    Non-model serializer to keep it flexible across custom user models.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data: dict[str, Any]) -> User:
        UserModel = get_user_model()
        return UserModel.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )


class ProfileSerializer(serializers.ModelSerializer):
    """
    Read-only profile payload with optional Rwanda-specific fields exposed
    as computed (safe) attributes so schema generation never breaks.
    """
    user_type = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    national_id = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "user_type",
            "phone_number",
            "national_id",
            "language",
            "district",
        )
        read_only_fields = fields

    def _maybe(self, obj: User, name: str) -> Optional[Any]:
        return getattr(obj, name, None) if hasattr(obj, name) else None

    def get_user_type(self, obj: User) -> Optional[str]:
        if hasattr(obj, "user_type"):
            return getattr(obj, "user_type")  # type: ignore[attr-defined]
        if getattr(obj, "driver_location", None):
            return "driver"
        return "passenger"

    def get_phone_number(self, obj: User) -> Optional[str]:
        return self._maybe(obj, "phone_number")

    def get_national_id(self, obj: User) -> Optional[str]:
        return self._maybe(obj, "national_id")

    def get_language(self, obj: User) -> Optional[str]:
        # e.g., "rw", "fr", "en"
        return self._maybe(obj, "language")

    def get_district(self, obj: User) -> Optional[str]:
        return self._maybe(obj, "district")


class ProfileUpdateSerializer(serializers.Serializer):

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
