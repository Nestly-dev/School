from django.urls import path
from .views import (
    RequestRideView,
    RideDetailView,
    RideHistoryView,
    MyRidesView,
)

app_name = "rides"

urlpatterns = [
    path("request/", RequestRideView.as_view(), name="request_ride"), 
    path("history/", RideHistoryView.as_view(), name="ride_history"),      
    path("mine/", MyRidesView.as_view(), name="my_rides"),                 
    path("<int:pk>/", RideDetailView.as_view(), name="ride_detail"),       
]
