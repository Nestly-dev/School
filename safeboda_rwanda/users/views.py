from __future__ import annotations

from typing import Any, Iterable, Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Optional local helpers; we fall back safely if they aren't present.
try:
    from .validators import (
        validate_rwanda_phone as _validate_phone,   # expected signature: (str) -> bool
        validate_national_id as _validate_nid,     # expected signature: (str) -> bool
    )
except Exception:  # pragma: no cover
    _validate_phone = None
    _validate_nid = None

try:
    from .constants import RWANDA_DISTRICTS  # e.g., ["Gasabo", "Kicukiro", ...]
except Exception:  # pragma: no cover
    RWANDA_DISTRICTS = [
    "Gasabo", "Kicukiro", "Nyarugenge",
    "Burera", "Gakenke", "Gicumbi", "Musanze", "Rulindo",
    "Gisagara", "Huye", "Kamonyi", "Muhanga", "Nyamagabe", "Nyanza", "Nyaruguru", "Ruhango",
    "Bugesera", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Nyagatare", "Rwamagana",
    "Karongi", "Ngororero", "Nyabihu", "Nyamasheke", "Rubavu", "Rusizi", "Rutsiro"
]


from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    RegistrationSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    UserListSerializer,
    DriverListSerializer,
)

User = get_user_model()


# ---------- Registration ----------

@extend_schema(
    request=RegistrationSerializer,
    responses={201: ProfileSerializer, 400: dict},
    examples=[
        OpenApiExample(
            "Register Rwanda user",
            value={
                "email": "user@example.com",
                "password": "StrongPass!123",
                "first_name": "Aline",
                "last_name": "Uwase",
            },
        )
    ],
    tags=["Users"],
)
class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(ProfileSerializer(user).data, status=status.HTTP_201_CREATED)


# ---------- Profile (GET / PUT) ----------

@extend_schema(
    responses={200: ProfileSerializer},
    tags=["Users"],
)
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(ProfileSerializer(request.user).data)

    @extend_schema(
        request=ProfileUpdateSerializer,
        responses={200: ProfileSerializer, 400: dict},
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user: Any = request.user
        # Only set attributes your model actually has
        for field, value in serializer.validated_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save(update_fields=[f for f in serializer.validated_data.keys() if hasattr(user, f)])

        return Response(ProfileSerializer(user).data)


# ---------- Districts ----------

@extend_schema(
    responses={200: dict},
    tags=["Users"],
)
class DistrictsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response({"districts": list(RWANDA_DISTRICTS)})


# ---------- Validation (Phone & National ID) ----------

def _fallback_phone_ok(phone: str) -> bool:
    """
    Simple Rwanda phone check:
    - allow +2507XXXXXXXX or 07XXXXXXXX (10 digits after leading 0)
    """
    import re
    return bool(re.fullmatch(r"(\+2507\d{8}|0?7\d{8})", phone))

def _fallback_nid_ok(nid: str) -> bool:
    """
    Basic Rwanda NID length check (commonly 16 digits).
    """
    return nid.isdigit() and len(nid) == 16


@extend_schema(
    request={"type": "object", "properties": {"phone": {"type": "string"}}, "required": ["phone"]},
    responses={200: {"type": "object", "properties": {"valid": {"type": "boolean"}, "formatted_phone": {"type": "string"}}}},
    examples=[OpenApiExample("Validate phone", value={"phone": "+250788123456"})],
    tags=["Users"],
)
class PhoneValidationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        phone = str(request.data.get("phone", "")).strip()
        if not phone:
            return Response({"detail": "phone is required"}, status=status.HTTP_400_BAD_REQUEST)

        if _validate_phone:
            ok = bool(_validate_phone(phone))  # type: ignore[misc]
        else:
            ok = _fallback_phone_ok(phone)

        formatted = phone
        if ok and not phone.startswith("+250"):
            # naive normalize to +250
            stripped = phone
            if stripped.startswith("0"):
                stripped = stripped[1:]
            formatted = "+250" + stripped

        return Response({"valid": ok, "formatted_phone": formatted})


@extend_schema(
    request={"type": "object", "properties": {"national_id": {"type": "string"}}, "required": ["national_id"]},
    responses={200: {"type": "object", "properties": {"valid": {"type": "boolean"}}}},
    examples=[OpenApiExample("Validate national id", value={"national_id": "1199999999999999"})],
    tags=["Users"],
)
class NationalIDValidationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        nid = str(request.data.get("national_id", "")).strip()
        if not nid:
            return Response({"detail": "national_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if _validate_nid:
            ok = bool(_validate_nid(nid))  # type: ignore[misc]
        else:
            ok = _fallback_nid_ok(nid)

        return Response({"valid": ok})


# ---------- Lists (Users & Drivers) ----------

@extend_schema(
    responses={200: UserListSerializer(many=True)},
    tags=["Users"],
)
class UsersListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserListSerializer

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.all().order_by("-date_joined")


@extend_schema(
    responses={200: DriverListSerializer(many=True)},
    tags=["Users"],
)
class DriversListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DriverListSerializer

    def get_queryset(self) -> QuerySet[User]:
        """
        Heuristic: treat users with an attached driver_location as drivers.
        This avoids depending on a 'user_type' DB column that may not exist.
        """
        return User.objects.filter(is_active=True, driver_location__isnull=False).order_by("id")
