"""
Serializers for Government Integration API
"""
from rest_framework import serializers
from .models import (
    RTDADriverReport,
    TaxReport,
    EmergencyIncident,
    ComplianceStatus,
    GovernmentAuditLog
)


class RTDADriverReportSerializer(serializers.ModelSerializer):
    """RTDA Driver License Verification"""

    driver_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = RTDADriverReport
        fields = [
            'id',
            'driver_id',
            'license_number',
            'license_type',
            'verification_status',
            'verification_date',
            'expiry_date',
            'rtda_reference',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'verification_status',
            'verification_date',
            'rtda_reference',
            'created_at',
            'updated_at'
        ]

    def validate_license_number(self, value):
        """Validate Rwanda license number format"""
        if not value.startswith('RW-'):
            raise serializers.ValidationError(
                "Rwanda license numbers must start with 'RW-'"
            )
        return value


class ComplianceStatusSerializer(serializers.ModelSerializer):
    """RTDA Compliance Status"""

    class Meta:
        model = ComplianceStatus
        fields = [
            'id',
            'category',
            'compliant',
            'compliance_percentage',
            'total_required',
            'total_compliant',
            'issues_identified',
            'action_plan',
            'last_audit_date',
            'next_audit_date',
            'created_at',
            'updated_at'
        ]


class TaxRevenueReportSerializer(serializers.Serializer):
    """Tax Revenue Report for RRA"""

    report_type = serializers.ChoiceField(
        choices=['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY'],
        required=True
    )
    period_start = serializers.DateField(required=True)
    period_end = serializers.DateField(required=True)

    # Output fields (read-only)
    total_rides = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    total_tax = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    driver_earnings = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    platform_commission = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    report_reference = serializers.CharField(read_only=True)

    def validate(self, data):
        """Validate date range"""
        if data['period_start'] > data['period_end']:
            raise serializers.ValidationError(
                "period_start must be before period_end"
            )
        return data


class EmergencyIncidentReportSerializer(serializers.ModelSerializer):
    """Emergency Incident Report"""

    ride_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = EmergencyIncident
        fields = [
            'id',
            'ride_id',
            'incident_type',
            'severity',
            'description',
            'location_lat',
            'location_lng',
            'location_address',
            'police_notified',
            'ambulance_called',
            'incident_reference',
            'authority_response',
            'resolved',
            'resolved_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'incident_reference',
            'authority_response',
            'resolved',
            'resolved_at',
            'created_at',
            'updated_at'
        ]

    def validate_description(self, value):
        """Ensure description is detailed enough"""
        if len(value) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters"
            )
        return value


class DataExportSerializer(serializers.Serializer):
    """Government Data Export"""

    start_date = serializers.DateField()
    end_date = serializers.DateField()
    data_type = serializers.ChoiceField(
        choices=['rides', 'drivers', 'analytics'],
        default='rides'
    )


class AuditLogSerializer(serializers.ModelSerializer):
    """Government Audit Log"""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = GovernmentAuditLog
        fields = [
            'id',
            'access_type',
            'endpoint',
            'user',
            'user_email',
            'user_name',
            'ip_address',
            'user_agent',
            'request_data',
            'response_status',
            'timestamp'
        ]
        read_only_fields = fields
