"""
Analytics Models for SafeBoda Rwanda
Business Intelligence and Reporting
"""
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class AnalyticsReport(models.Model):
    """Store generated analytics reports for caching"""

    class ReportType(models.TextChoices):
        RIDE_PATTERNS = "RIDE_PATTERNS", "Ride Patterns"
        DRIVER_PERFORMANCE = "DRIVER_PERFORMANCE", "Driver Performance"
        REVENUE = "REVENUE", "Revenue Summary"
        TRAFFIC = "TRAFFIC", "Traffic Analysis"
        USER_BEHAVIOR = "USER_BEHAVIOR", "User Behavior"
        CUSTOM = "CUSTOM", "Custom Report"

    report_type = models.CharField(
        max_length=30,
        choices=ReportType.choices
    )
    title = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
    report_data = models.JSONField()
    generated_by = models.ForeignKey(
        User,
        related_name="generated_reports",
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["report_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.report_type} - {self.title}"
