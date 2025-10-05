from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class RideStatus(models.TextChoices):
    REQUESTED = "REQUESTED", "Requested"
    ACCEPTED  = "ACCEPTED",  "Accepted"
    ONGOING   = "ONGOING",   "Ongoing"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"

class Ride(models.Model):
    rider = models.ForeignKey(User, related_name="rides_as_rider", on_delete=models.CASCADE)
    driver = models.ForeignKey(User, related_name="rides_as_driver", on_delete=models.SET_NULL, null=True, blank=True)

    pickup_address = models.CharField(max_length=255, blank=True)
    dropoff_address = models.CharField(max_length=255, blank=True)

    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lat = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = models.DecimalField(max_digits=9, decimal_places=6)

    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fare_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=12, choices=RideStatus.choices, default=RideStatus.REQUESTED)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Ride #{self.pk} {self.status} (rider={self.rider_id}, driver={self.driver_id})"

    @staticmethod
    def price_for(distance_km: Decimal, base=Decimal("500"), per_km=Decimal("800")) -> Decimal:
        # simple RWF pricing model: base + per_km * distance
        amount = base + (per_km * (distance_km or Decimal("0")))
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
