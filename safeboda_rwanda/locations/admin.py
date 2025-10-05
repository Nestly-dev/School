from django.contrib import admin
from .models import DriverLocation, LocationPing


@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "lat",
        "lng",
        "is_online",
        "speed_kmh",
        "updated_at",
    )
    list_filter = ("is_online",)
    search_fields = ("driver__username", "driver__email")
    readonly_fields = ("updated_at", "created_at")


@admin.register(LocationPing)
class LocationPingAdmin(admin.ModelAdmin):
    list_display = ("driver", "lat", "lng", "speed_kmh", "created_at")
    list_filter = ("created_at",)
    search_fields = ("driver__username", "driver__email")
    readonly_fields = ("created_at",)
