"""
Government Integration Models for SafeBoda Rwanda
Handles RTDA reporting, compliance, and emergency services
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class RTDADriverReport(models.Model):
    """RTDA Driver License Verification Reports"""

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Verification"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "License Expired"

    driver = models.ForeignKey(
        User,
        related_name="rtda_verifications",
        on_delete=models.CASCADE
    )
    license_number = models.CharField(max_length=50)
    license_type = models.CharField(max_length=20, default="MOTORCYCLE")
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    rtda_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["driver", "-created_at"]),
            models.Index(fields=["verification_status"]),
        ]

    def __str__(self):
        return f"RTDA Verification for Driver {self.driver_id} - {self.verification_status}"


class TaxReport(models.Model):
    """Tax Revenue Reports for Rwanda Revenue Authority"""

    class ReportType(models.TextChoices):
        DAILY = "DAILY", "Daily Report"
        WEEKLY = "WEEKLY", "Weekly Report"
        MONTHLY = "MONTHLY", "Monthly Report"
        QUARTERLY = "QUARTERLY", "Quarterly Report"

    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_rides = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_tax = models.DecimalField(max_digits=15, decimal_places=2)
    driver_earnings = models.DecimalField(max_digits=15, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=15, decimal_places=2)
    report_reference = models.CharField(max_length=100, unique=True)
    submitted_to_rra = models.BooleanField(default=False)
    submission_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-period_end",)
        indexes = [
            models.Index(fields=["-period_end"]),
            models.Index(fields=["report_type", "-period_end"]),
        ]

    def __str__(self):
        return f"{self.report_type} Tax Report: {self.period_start} to {self.period_end}"


class EmergencyIncident(models.Model):
    """Emergency Incident Reports for Government Authorities"""

    class IncidentType(models.TextChoices):
        ACCIDENT = "ACCIDENT", "Accident"
        MEDICAL = "MEDICAL", "Medical Emergency"
        CRIME = "CRIME", "Crime/Security Issue"
        BREAKDOWN = "BREAKDOWN", "Vehicle Breakdown"
        OTHER = "OTHER", "Other Emergency"

    class SeverityLevel(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    ride = models.ForeignKey(
        "rides.Ride",
        related_name="emergency_incidents",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    reporter = models.ForeignKey(
        User,
        related_name="reported_incidents",
        on_delete=models.SET_NULL,
        null=True
    )
    incident_type = models.CharField(
        max_length=20,
        choices=IncidentType.choices
    )
    severity = models.CharField(
        max_length=20,
        choices=SeverityLevel.choices
    )
    description = models.TextField()
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6)
    location_address = models.CharField(max_length=255, blank=True)
    police_notified = models.BooleanField(default=False)
    ambulance_called = models.BooleanField(default=False)
    incident_reference = models.CharField(max_length=100, unique=True)
    authority_response = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["incident_type", "severity"]),
            models.Index(fields=["resolved"]),
        ]

    def __str__(self):
        return f"{self.incident_type} Incident - {self.incident_reference}"


class ComplianceStatus(models.Model):
    """Track SafeBoda compliance with RTDA regulations"""

    class ComplianceCategory(models.TextChoices):
        DRIVER_LICENSING = "DRIVER_LICENSING", "Driver Licensing"
        VEHICLE_INSPECTION = "VEHICLE_INSPECTION", "Vehicle Inspection"
        INSURANCE = "INSURANCE", "Insurance Coverage"
        SAFETY_STANDARDS = "SAFETY_STANDARDS", "Safety Standards"
        REPORTING = "REPORTING", "Government Reporting"

    category = models.CharField(
        max_length=30,
        choices=ComplianceCategory.choices
    )
    compliant = models.BooleanField(default=True)
    compliance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00
    )
    total_required = models.IntegerField(default=0)
    total_compliant = models.IntegerField(default=0)
    issues_identified = models.TextField(blank=True)
    action_plan = models.TextField(blank=True)
    last_audit_date = models.DateField()
    next_audit_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-last_audit_date",)
        verbose_name_plural = "Compliance statuses"

    def __str__(self):
        return f"{self.category} - {self.compliance_percentage}%"


class GovernmentAuditLog(models.Model):
    """Audit trail for government data access"""

    class AccessType(models.TextChoices):
        REPORT_GENERATED = "REPORT_GENERATED", "Report Generated"
        DATA_EXPORTED = "DATA_EXPORTED", "Data Exported"
        VERIFICATION_REQUESTED = "VERIFICATION_REQUESTED", "Verification Requested"
        INCIDENT_REPORTED = "INCIDENT_REPORTED", "Incident Reported"
        COMPLIANCE_CHECK = "COMPLIANCE_CHECK", "Compliance Check"

    access_type = models.CharField(
        max_length=30,
        choices=AccessType.choices
    )
    endpoint = models.CharField(max_length=200)
    user = models.ForeignKey(
        User,
        related_name="government_accesses",
        on_delete=models.SET_NULL,
        null=True
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    response_status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["access_type", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.access_type} by {self.user} at {self.timestamp}"
