"""
URL configuration for rides app - all booking and tracking endpoints
"""
from django.urls import path
from .views import (
    CreateBookingView,
    BookingDetailView,
    UpdateBookingStatusView,
    CancelBookingView,
    ActiveBookingsView,
    ProcessPaymentView,
    RealTimeTrackingView,
    UpdateDriverLocationView,
    NotificationsView,
    MarkNotificationReadView,
    SendNotificationView,
    RequestRideView,
    RideDetailView,
    RideHistoryView,
    MyRidesView,
)
from .admin_views import (
    AdminRideReportsView,
    AdminDriverReportsView,
    SystemDashboardView,
    MarkRTDAReportedView,
    RTDAComplianceExportView,
)

app_name = "rides"

urlpatterns = [
    # Booking Endpoints (Task 1)
    path("bookings/create/", CreateBookingView.as_view(), name="create-booking"),
    path("bookings/<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<int:pk>/status/", UpdateBookingStatusView.as_view(), name="update-booking-status"),
    path("bookings/<int:pk>/cancel/", CancelBookingView.as_view(), name="cancel-booking"),
    path("bookings/active/", ActiveBookingsView.as_view(), name="active-bookings"),
    
    # Payment Endpoints
    path("payments/process/", ProcessPaymentView.as_view(), name="process-payment"),
    
    # Real-Time Tracking
    path("realtime/tracking/<int:booking_id>/", RealTimeTrackingView.as_view(), name="realtime-tracking"),
    path("realtime/location/update/", UpdateDriverLocationView.as_view(), name="update-driver-location"),
    
    # Notifications
    path("notifications/", NotificationsView.as_view(), name="notifications"),
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),
    path("notifications/send/", SendNotificationView.as_view(), name="send-notification"),
    
    # Legacy endpoints (backward compatibility)
    path("request/", RequestRideView.as_view(), name="request_ride"),
    path("history/", RideHistoryView.as_view(), name="ride_history"),
    path("mine/", MyRidesView.as_view(), name="my_rides"),
    path("<int:pk>/", RideDetailView.as_view(), name="ride_detail"),
    
    # Administrative Reports (Task 1)
    path("admin/reports/rides/", AdminRideReportsView.as_view(), name="admin-ride-reports"),
    path("admin/reports/drivers/", AdminDriverReportsView.as_view(), name="admin-driver-reports"),
    path("admin/dashboard/", SystemDashboardView.as_view(), name="system-dashboard"),
    path("admin/reports/rtda/mark-reported/", MarkRTDAReportedView.as_view(), name="mark-rtda-reported"),
    path("admin/reports/rtda/export/", RTDAComplianceExportView.as_view(), name="rtda-export"),
]