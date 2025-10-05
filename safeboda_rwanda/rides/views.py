from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, status, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Ride  # make sure your Ride model matches the field names used here

User = get_user_model()


# ---------- Serializers ----------

class RequestRideSerializer(serializers.ModelSerializer):
    """
    Fields to create a ride request.
    Adjust to match your Ride model if names differ.
    """
    class Meta:
        model = Ride
        fields = [
            "pickup_lat",
            "pickup_lng",
            "dropoff_lat",
            "dropoff_lng",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return Ride.objects.create(rider=user, status="requested", **validated_data)


class RideSerializer(serializers.ModelSerializer):
    rider_email = serializers.EmailField(source="rider.email", read_only=True)
    driver_email = serializers.EmailField(source="driver.email", read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id",
            "status",
            "rider",
            "rider_email",
            "driver",
            "driver_email",
            "pickup_lat",
            "pickup_lng",
            "dropoff_lat",
            "dropoff_lng",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "rider",
            "driver",
            "created_at",
            "updated_at",
        ]


# ---------- Pagination ----------

class SmallPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100


# ---------- Views ----------

class RequestRideView(APIView):
    """
    POST /api/rides/request/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Optional guard: only passengers may request
        if getattr(request.user, "user_type", None) and request.user.user_type != "passenger":
            return Response(
                {"detail": "Only passengers can request rides."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RequestRideSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        return Response(RideSerializer(ride).data, status=status.HTTP_201_CREATED)


class RideDetailView(generics.RetrieveAPIView):
    """
    GET /api/rides/<int:pk>/
    """
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]


class RideHistoryView(generics.ListAPIView):
    """
    GET /api/rides/history/?page=1&limit=20&status=completed
    Shows rides where the user is rider or driver.
    """
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SmallPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        qs = Ride.objects.filter(Q(rider=user) | Q(driver=user)).order_by("-created_at")

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs


class MyRidesView(generics.ListAPIView):
    """
    GET /api/rides/mine/?role=rider|driver|both&status=<status>&page=1&limit=10
    Defaults to role=both.
    """
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SmallPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        role = (self.request.query_params.get("role") or "both").lower()

        if role == "rider":
            qs = Ride.objects.filter(rider=user)
        elif role == "driver":
            qs = Ride.objects.filter(driver=user)
        else:
            qs = Ride.objects.filter(Q(rider=user) | Q(driver=user))

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.order_by("-created_at")
