"""
Government Integration API Endpoints for SafeBoda Rwanda
Handles RTDA reporting, tax compliance, and emergency services
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .models import (
    RTDADriverReport,
    TaxReport,
    EmergencyIncident,
    ComplianceStatus,
    GovernmentAuditLog
)
from .serializers import (
    RTDADriverReportSerializer,
    ComplianceStatusSerializer,
    TaxRevenueReportSerializer,
    EmergencyIncidentReportSerializer,
    DataExportSerializer,
    AuditLogSerializer
)
from .services import GovernmentIntegrationService
from rides.models import Ride, RideStatus

logger = logging.getLogger(__name__)


class RTDADriverVerificationView(APIView):
    """
    POST /api/government/rtda/driver-report/
    Submit driver license verification request to RTDA
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Government Integration"],
        request=RTDADriverReportSerializer,
        responses={201: RTDADriverReportSerializer, 400: dict},
        summary="Submit driver license verification to RTDA",
        description="""
        Submit driver license verification request to Rwanda Transport Development Agency (RTDA).

        This endpoint:
        - Validates driver license number format
        - Submits verification request to RTDA API
        - Creates audit trail for compliance
        - Returns verification status

        Rwanda license format: RW-XXXXX-XXXX
        """,
        examples=[
            OpenApiExample(
                "Driver Verification Request",
                value={
                    "driver_id": 123,
                    "license_number": "RW-12345-6789",
                    "license_type": "MOTORCYCLE"
                }
            )
        ]
    )
    def post(self, request):
        serializer = RTDADriverReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Submit to RTDA
        result = GovernmentIntegrationService.verify_driver_license(
            driver_id=serializer.validated_data['driver_id'],
            license_number=serializer.validated_data['license_number'],
            license_type=serializer.validated_data.get('license_type', 'MOTORCYCLE')
        )

        # Create audit log
        self._log_government_access(
            request,
            'VERIFICATION_REQUESTED',
            result.get('success', False)
        )

        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Verification failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'success': True,
                'verification': RTDADriverReportSerializer(result['report']).data,
                'message': 'Driver verification submitted to RTDA'
            },
            status=status.HTTP_201_CREATED
        )

    def _log_government_access(self, request, access_type, success):
        """Create audit trail"""
        GovernmentAuditLog.objects.create(
            access_type=access_type,
            endpoint=request.path,
            user=request.user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_data=request.data,
            response_status=201 if success else 400
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ComplianceStatusView(APIView):
    """
    GET /api/government/rtda/compliance-status/
    Get current RTDA compliance status
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Government Integration"],
        responses={200: ComplianceStatusSerializer(many=True)},
        summary="Get RTDA compliance status",
        description="""
        Retrieve current compliance status with RTDA regulations.

        Returns compliance metrics for:
        - Driver licensing (all drivers have valid licenses)
        - Vehicle inspection (all vehicles properly inspected)
        - Insurance coverage (comprehensive coverage)
        - Safety standards (helmet provision, GPS tracking)
        - Government reporting (timely submission of reports)

        Required for RTDA operational license maintenance.
        """,
        parameters=[
            OpenApiParameter(
                name='category',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by compliance category',
                required=False
            )
        ]
    )
    def get(self, request):
        category = request.query_params.get('category')

        # Get or create compliance status records
        compliance_data = GovernmentIntegrationService.get_compliance_status(category)

        # Create audit log
        GovernmentAuditLog.objects.create(
            access_type='COMPLIANCE_CHECK',
            endpoint=request.path,
            user=request.user,
            ip_address=self._get_client_ip(request),
            response_status=200
        )

        return Response({
            'compliance_overview': compliance_data,
            'overall_compliant': all(
                item.get('compliant', False) for item in compliance_data
            ),
            'last_updated': timezone.now().isoformat()
        })

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class TaxRevenueReportView(APIView):
    """
    POST /api/government/tax/revenue-report/
    Generate and submit tax revenue report
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Government Integration"],
        request=TaxRevenueReportSerializer,
        responses={201: TaxRevenueReportSerializer, 400: dict},
        summary="Generate tax revenue report for RRA",
        description="""
        Generate and submit tax revenue report to Rwanda Revenue Authority (RRA).

        Calculates:
        - Total rides and revenue for period
        - VAT (18% on platform commission)
        - Withholding tax on driver earnings
        - Platform commission breakdown

        Report types: DAILY, WEEKLY, MONTHLY, QUARTERLY

        Required for tax compliance with Rwanda Revenue Authority.
        """,
        examples=[
            OpenApiExample(
                "Monthly Tax Report",
                value={
                    "report_type": "MONTHLY",
                    "period_start": "2025-09-01",
                    "period_end": "2025-09-30"
                }
            )
        ]
    )
    def post(self, request):
        serializer = TaxRevenueReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate tax report
        result = GovernmentIntegrationService.generate_tax_report(
            report_type=serializer.validated_data['report_type'],
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end']
        )

        # Create audit log
        GovernmentAuditLog.objects.create(
            access_type='REPORT_GENERATED',
            endpoint=request.path,
            user=request.user,
            ip_address=self._get_client_ip(request),
            request_data=request.data,
            response_status=201 if result.get('success') else 400
        )

        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Report generation failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'success': True,
                'report': result['report_data'],
                'message': 'Tax report generated successfully'
            },
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EmergencyIncidentReportView(APIView):
    """
    POST /api/government/emergency/incident-report/
    Report emergency incident to authorities
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Government Integration"],
        request=EmergencyIncidentReportSerializer,
        responses={201: EmergencyIncidentReportSerializer, 400: dict},
        summary="Report emergency incident to authorities",
        description="""
        Report emergency incidents to relevant Rwanda authorities:
        - Rwanda National Police (accidents, crimes)
        - Emergency medical services (medical emergencies)
        - RTDA (serious transport incidents)

        Incident types: ACCIDENT, MEDICAL, CRIME, BREAKDOWN, OTHER
        Severity levels: LOW, MEDIUM, HIGH, CRITICAL

        Critical incidents automatically notify:
        - Police: +250 112
        - Ambulance: +250 912
        - RTDA Emergency Line
        """,
        examples=[
            OpenApiExample(
                "Accident Report",
                value={
                    "ride_id": 456,
                    "incident_type": "ACCIDENT",
                    "severity": "HIGH",
                    "description": "Minor collision at roundabout",
                    "location_lat": -1.9536,
                    "location_lng": 30.0606,
                    "police_notified": True,
                    "ambulance_called": False
                }
            )
        ]
    )
    def post(self, request):
        serializer = EmergencyIncidentReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create incident report
        result = GovernmentIntegrationService.report_emergency_incident(
            reporter=request.user,
            ride_id=serializer.validated_data.get('ride_id'),
            incident_type=serializer.validated_data['incident_type'],
            severity=serializer.validated_data['severity'],
            description=serializer.validated_data['description'],
            location_lat=serializer.validated_data['location_lat'],
            location_lng=serializer.validated_data['location_lng'],
            police_notified=serializer.validated_data.get('police_notified', False),
            ambulance_called=serializer.validated_data.get('ambulance_called', False)
        )

        # Create audit log
        GovernmentAuditLog.objects.create(
            access_type='INCIDENT_REPORTED',
            endpoint=request.path,
            user=request.user,
            ip_address=self._get_client_ip(request),
            request_data=request.data,
            response_status=201 if result.get('success') else 400
        )

        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Incident report failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'success': True,
                'incident': EmergencyIncidentReportSerializer(result['incident']).data,
                'emergency_contacts': {
                    'police': '+250 112',
                    'ambulance': '+250 912',
                    'rtda_emergency': '+250 788 123 000'
                },
                'message': 'Incident reported to authorities'
            },
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GovernmentDataExportView(APIView):
    """
    GET /api/government/data/export-request/
    Export ride data for government analysis
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Government Integration"],
        responses={200: DataExportSerializer, 400: dict},
        summary="Export ride data for government analysis",
        description="""
        Export anonymized ride data for government transport analysis.

        Data sovereignty: All data remains in Rwanda and complies with data protection laws.

        Exported data includes:
        - Ride patterns and routes (anonymized)
        - Traffic congestion hotspots
        - Peak hour analysis
        - Safety metrics
        - Economic impact data

        Used by:
        - RTDA for transport planning
        - City of Kigali for traffic management
        - MININFRA for infrastructure development
        """,
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Export start date (YYYY-MM-DD)',
                required=True
            ),
            OpenApiParameter(
                name='end_date',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Export end date (YYYY-MM-DD)',
                required=True
            ),
            OpenApiParameter(
                name='data_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Type of data to export: rides, drivers, analytics',
                required=False
            )
        ]
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        data_type = request.query_params.get('data_type', 'rides')

        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Export data
        result = GovernmentIntegrationService.export_government_data(
            start_date=start_date,
            end_date=end_date,
            data_type=data_type
        )

        # Create audit log
        GovernmentAuditLog.objects.create(
            access_type='DATA_EXPORTED',
            endpoint=request.path,
            user=request.user,
            ip_address=self._get_client_ip(request),
            request_data={'start_date': start_date, 'end_date': end_date, 'data_type': data_type},
            response_status=200 if result.get('success') else 400
        )

        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Data export failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'success': True,
            'export_data': result['data'],
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'data_type': data_type,
                'record_count': result.get('count', 0),
                'generated_at': timezone.now().isoformat()
            },
            'data_sovereignty': 'All data stored and processed in Rwanda',
            'message': 'Data export completed successfully'
        })

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GovernmentAuditLogView(generics.ListAPIView):
    """
    POST /api/government/audit/access-log/
    Get government audit trail
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AuditLogSerializer

    @extend_schema(
        tags=["Government Integration"],
        responses={200: AuditLogSerializer(many=True)},
        summary="Get government data access audit trail",
        description="""
        Retrieve complete audit trail of government data access.

        Tracks all:
        - Report generations
        - Data exports
        - Verification requests
        - Compliance checks

        Required for:
        - GDPR-equivalent Rwanda data protection compliance
        - Security audits
        - Transparency reporting
        - Government accountability
        """,
        parameters=[
            OpenApiParameter(
                name='access_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by access type',
                required=False
            ),
            OpenApiParameter(
                name='days',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of days to look back (default: 30)',
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        access_type = self.request.query_params.get('access_type')
        days = int(self.request.query_params.get('days', 30))

        queryset = GovernmentAuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=days)
        ).select_related('user').order_by('-timestamp')

        if access_type:
            queryset = queryset.filter(access_type=access_type)

        return queryset
