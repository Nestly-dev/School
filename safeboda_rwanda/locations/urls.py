from django.urls import path
from .views import (
    NearbyDriversView,
    CalculateDistanceView,
    ReverseGeocodeView,
    BatchProcessView,
    DriverUpdateLocationView,
    DriverCurrentLocationView,
    PopularLocationsView,  # NEW
)

app_name = "locations"

urlpatterns = [
    path("drivers/nearby/", NearbyDriversView.as_view(), name="drivers-nearby"),
    path("calculate-distance/", CalculateDistanceView.as_view(), name="calculate-distance"),
    path("reverse-geocode/", ReverseGeocodeView.as_view(), name="reverse-geocode"),
    path("batch-process/", BatchProcessView.as_view(), name="batch-process"),
    path("driver/update/", DriverUpdateLocationView.as_view(), name="driver-update"),
    path("driver/current/", DriverCurrentLocationView.as_view(), name="driver-current"),
    path("popular/", PopularLocationsView.as_view(), name="popular"),  # NEW
]
