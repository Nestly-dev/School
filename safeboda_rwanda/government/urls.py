"""
Government Integration API URLs
"""
from django.urls import path
from . import views

app_name = 'government'

urlpatterns = [
    # RTDA Integration
    path(
        'rtda/driver-report/',
        views.RTDADriverVerificationView.as_view(),
        name='rtda-driver-verification'
    ),
    path(
        'rtda/compliance-status/',
        views.ComplianceStatusView.as_view(),
        name='compliance-status'
    ),

    # Tax Reporting
    path(
        'tax/revenue-report/',
        views.TaxRevenueReportView.as_view(),
        name='tax-revenue-report'
    ),

    # Emergency Services
    path(
        'emergency/incident-report/',
        views.EmergencyIncidentReportView.as_view(),
        name='emergency-incident-report'
    ),

    # Data Export & Audit
    path(
        'data/export-request/',
        views.GovernmentDataExportView.as_view(),
        name='data-export'
    ),
    path(
        'audit/access-log/',
        views.GovernmentAuditLogView.as_view(),
        name='audit-log'
    ),
]
