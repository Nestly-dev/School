from decimal import Decimal
from math import radians, sin, cos, asin, sqrt
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ride, RideStatus

User = get_user_model()

def haversine_km(lat1, lon1, lat2, lon2) -> Decimal:
    # all args as Decimal or float
    R = 6371.0  # km
    φ1, φ2 = radians(float(lat1)), radians(float(lat2))
    Δφ = radians(float(lat2) - float(lat1))
    Δλ = radians(float(lon2) - float(lon1))
    a = sin(Δφ/2)**2 + cos(φ1)*cos(φ2)*sin(Δλ/2)**2
    c = 2 * asin(sqrt(a))
    return Decimal(str(R * c)).quantize(Decimal("0.01"))

class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = (
            "id", "pickup_address", "dropoff_address",
            "pickup_lat", "pickup_lng", "dropoff_lat", "dropoff_lng",
            "distance_km", "fare_estimate", "status", "created_at",
        )
        read_only_fields = ("id","distance_km","fare_estimate","status","created_at")

    def create(self, validated):
        user = self.context["request"].user
        validated["rider"] = user
        dist = haversine_km(validated["pickup_lat"], validated["pickup_lng"],
                            validated["dropoff_lat"], validated["dropoff_lng"])
        validated["distance_km"] = dist
        validated["fare_estimate"] = Ride.price_for(dist)
        return Ride.objects.create(**validated)

class RideListItemSerializer(serializers.ModelSerializer):
    rider = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    class Meta:
        model = Ride
        fields = ("id","status","fare_estimate","distance_km",
                  "pickup_address","dropoff_address","rider","driver","created_at")
    def get_rider(self, obj):  return {"id":obj.rider_id, "username":getattr(obj.rider,"username",None)}
    def get_driver(self, obj): return {"id":obj.driver_id, "username":getattr(obj.driver,"username",None)}

class RideDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = "__all__"
        read_only_fields = ("rider","driver","distance_km","fare_estimate","status","created_at","updated_at","started_at","completed_at")

class AcceptRideSerializer(serializers.Serializer):
    def validate(self, attrs):
        ride: Ride = self.context["ride"]
        if ride.status != RideStatus.REQUESTED:
            raise serializers.ValidationError("Ride is not available to accept.")
        return attrs
    def save(self, **kwargs):
        ride: Ride = self.context["ride"]
        ride.driver = self.context["request"].user
        ride.status = RideStatus.ACCEPTED
        ride.save(update_fields=["driver","status","updated_at"])
        return ride

class StartRideSerializer(serializers.Serializer):
    def validate(self, attrs):
        ride: Ride = self.context["ride"]
        if ride.status != RideStatus.ACCEPTED:
            raise serializers.ValidationError("Ride is not in ACCEPTED state.")
        if ride.driver_id != self.context["request"].user.id:
            raise serializers.ValidationError("Only the assigned driver can start the ride.")
        return attrs
    def save(self, **kwargs):
        ride: Ride = self.context["ride"]
        ride.status = RideStatus.ONGOING
        ride.started_at = timezone.now()
        ride.save(update_fields=["status","started_at","updated_at"])
        return ride

class CompleteRideSerializer(serializers.Serializer):
    def validate(self, attrs):
        ride: Ride = self.context["ride"]
        if ride.status != RideStatus.ONGOING:
            raise serializers.ValidationError("Ride is not ONGOING.")
        if ride.driver_id != self.context["request"].user.id:
            raise serializers.ValidationError("Only the assigned driver can complete the ride.")
        return attrs
    def save(self, **kwargs):
        ride: Ride = self.context["ride"]
        ride.status = RideStatus.COMPLETED
        ride.completed_at = timezone.now()
        ride.save(update_fields=["status","completed_at","updated_at"])
        return ride

class CancelRideSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    def validate(self, attrs):
        ride: Ride = self.context["ride"]
        user = self.context["request"].user
        if ride.status in (RideStatus.COMPLETED, RideStatus.CANCELLED):
            raise serializers.ValidationError("Ride is already finished.")
        if user.id not in (ride.rider_id, ride.driver_id):
            raise serializers.ValidationError("You are not part of this ride.")
        return attrs
    def save(self, **kwargs):
        ride: Ride = self.context["ride"]
        ride.status = RideStatus.CANCELLED
        ride.cancel_reason = self.validated_data.get("reason","")
        ride.save(update_fields=["status","cancel_reason","updated_at"])
        return ride
