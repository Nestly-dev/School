"""
Monitoring & Production Readiness URLs
"""
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Health Check
    path(
        'detailed/',
        views.DetailedHealthCheckView.as_view(),
        name='health-detailed'
    ),

    # Monitoring
    path(
        'metrics/',
        views.SystemMetricsView.as_view(),
        name='system-metrics'
    ),
    path(
        'logs/',
        views.ApplicationLogsView.as_view(),
        name='application-logs'
    ),

    # Admin Operations
    path(
        'backup/trigger/',
        views.TriggerBackupView.as_view(),
        name='backup-trigger'
    ),
    path(
        'system/status/',
        views.SystemStatusView.as_view(),
        name='system-status'
    ),
    path(
        'maintenance/enable/',
        views.MaintenanceModeView.as_view(),
        name='maintenance-mode'
    ),
]
