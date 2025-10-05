from django.conf import settings
from django.db import models


class DriverLocation(models.Model):
    """
    One row per driver to keep their latest location.
    """
    driver = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_location",
    )
    lat = models.FloatField()
    lng = models.FloatField()
    is_online = models.BooleanField(default=True)
    speed_kmh = models.FloatField(default=0, help_text="Last reported speed")
    heading = models.FloatField(null=True, blank=True, help_text="Degrees 0-359")
    accuracy_m = models.FloatField(null=True, blank=True)

    # timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "locations_driver_location"
        indexes = [
            models.Index(fields=["is_online", "updated_at"]),
            models.Index(fields=["lat", "lng"]),
        ]

    def __str__(self) -> str:
        return f"{self.driver_id} @ ({self.lat}, {self.lng})"


class LocationPing(models.Model):
    """
    Historical breadcrumb of pings (optional, useful for debugging/analytics).
    """
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="location_pings",
    )
    lat = models.FloatField()
    lng = models.FloatField()
    speed_kmh = models.FloatField(default=0)
    heading = models.FloatField(null=True, blank=True)
    accuracy_m = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "locations_location_ping"
        indexes = [models.Index(fields=["driver", "created_at"])]

    def __str__(self) -> str:
        return f"Ping {self.driver_id} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
