"""
Analytics & Business Intelligence API URLs
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Ride Patterns
    path(
        'rides/patterns/',
        views.RidePatternsAnalyticsView.as_view(),
        name='ride-patterns'
    ),

    # Driver Performance
    path(
        'drivers/performance/',
        views.DriverPerformanceAnalyticsView.as_view(),
        name='driver-performance'
    ),

    # Revenue Analytics
    path(
        'revenue/summary/',
        views.RevenueSummaryAnalyticsView.as_view(),
        name='revenue-summary'
    ),

    # Traffic Hotspots
    path(
        'traffic/hotspots/',
        views.TrafficHotspotsAnalyticsView.as_view(),
        name='traffic-hotspots'
    ),

    # User Behavior
    path(
        'users/behavior/',
        views.UserBehaviorAnalyticsView.as_view(),
        name='user-behavior'
    ),

    # Custom Reports
    path(
        'reports/generate/',
        views.CustomReportGeneratorView.as_view(),
        name='generate-report'
    ),
]
