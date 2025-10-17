"""
Analytics & Business Intelligence API Endpoints
For SafeBoda Rwanda data-driven decision making
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .services import AnalyticsService
from .serializers import (
    RidePatternsSerializer,
    DriverPerformanceSerializer,
    RevenueSummarySerializer,
    TrafficHotspotsSerializer,
    UserBehaviorSerializer,
    CustomReportSerializer
)
from rides.models import Ride, RideStatus

logger = logging.getLogger(__name__)


class RidePatternsAnalyticsView(APIView):
    """
    GET /api/analytics/rides/patterns/
    Analyze ride patterns and trends
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        responses={200: RidePatternsSerializer},
        summary="Analyze ride patterns and trends",
        description="""
        Comprehensive ride pattern analysis for business intelligence:

        - Daily/weekly/monthly ride volume trends
        - Peak hour identification
        - Day-of-week patterns
        - Seasonal variations
        - Route popularity analysis
        - Cancellation rate trends

        Used for:
        - Driver resource allocation
        - Dynamic pricing strategies
        - Marketing campaign timing
        - Service expansion planning
        """,
        parameters=[
            OpenApiParameter(
                name='period',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Analysis period: 7days, 30days, 90days, 1year (default: 30days)',
                required=False
            ),
            OpenApiParameter(
                name='granularity',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Data granularity: hour, day, week, month (default: day)',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get('period', '30days')
        granularity = request.query_params.get('granularity', 'day')

        analytics = AnalyticsService.analyze_ride_patterns(period, granularity)

        return Response({
            'success': True,
            'period': period,
            'granularity': granularity,
            'analytics': analytics,
            'generated_at': timezone.now().isoformat()
        })


class DriverPerformanceAnalyticsView(APIView):
    """
    GET /api/analytics/drivers/performance/
    Analyze driver performance metrics
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        responses={200: DriverPerformanceSerializer(many=True)},
        summary="Analyze driver performance metrics",
        description="""
        Driver performance analytics for quality assurance:

        Metrics tracked:
        - Total rides completed
        - Average customer rating
        - Acceptance rate (rides accepted vs offered)
        - Cancellation rate
        - Average earnings per hour
        - Online time vs ride time efficiency
        - Peak hour activity

        Used for:
        - Driver incentive programs
        - Quality improvement initiatives
        - Top performer identification
        - Driver training needs assessment
        """,
        parameters=[
            OpenApiParameter(
                name='period',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Analysis period: 7days, 30days, 90days (default: 30days)',
                required=False
            ),
            OpenApiParameter(
                name='top_n',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of top performers to return (default: 20)',
                required=False
            ),
            OpenApiParameter(
                name='metric',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Sort by metric: rides, earnings, rating (default: rides)',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get('period', '30days')
        top_n = int(request.query_params.get('top_n', 20))
        metric = request.query_params.get('metric', 'rides')

        analytics = AnalyticsService.analyze_driver_performance(period, top_n, metric)

        return Response({
            'success': True,
            'period': period,
            'top_n': top_n,
            'sort_metric': metric,
            'driver_performance': analytics,
            'generated_at': timezone.now().isoformat()
        })


class RevenueSummaryAnalyticsView(APIView):
    """
    GET /api/analytics/revenue/summary/
    Revenue and financial analytics
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        responses={200: RevenueSummarySerializer},
        summary="Revenue and financial analytics",
        description="""
        Comprehensive revenue analytics for financial planning:

        Financial Metrics:
        - Total Gross Revenue (RWF)
        - Platform Commission (20%)
        - Driver Earnings (80%)
        - Average Fare per Ride
        - Revenue Growth Rate
        - Revenue by Payment Method (MTN MoMo, Airtel Money, Cash)

        Time-based Analysis:
        - Daily revenue trends
        - Month-over-month growth
        - Revenue forecast

        Geographic Analysis:
        - Revenue by area/district
        - High-value routes

        Used for:
        - Financial reporting to stakeholders
        - Budget planning and forecasting
        - Pricing strategy optimization
        - Tax reporting preparation
        """,
        parameters=[
            OpenApiParameter(
                name='period',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Analysis period: 7days, 30days, 90days, 1year (default: 30days)',
                required=False
            ),
            OpenApiParameter(
                name='breakdown',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Breakdown by: day, week, month, payment_method (default: day)',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get('period', '30days')
        breakdown = request.query_params.get('breakdown', 'day')

        analytics = AnalyticsService.analyze_revenue(period, breakdown)

        return Response({
            'success': True,
            'period': period,
            'breakdown': breakdown,
            'revenue_analytics': analytics,
            'currency': 'RWF',
            'generated_at': timezone.now().isoformat()
        })


class TrafficHotspotsAnalyticsView(APIView):
    """
    GET /api/analytics/traffic/hotspots/
    Traffic pattern and hotspot analysis
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        responses={200: TrafficHotspotsSerializer},
        summary="Traffic pattern and hotspot analysis",
        description="""
        Geographic and traffic pattern analysis for operational optimization:

        Hotspot Identification:
        - Popular pickup locations
        - Common dropoff destinations
        - High-density route corridors
        - Underserved areas

        Time-based Patterns:
        - Peak hour traffic by location
        - Event-based surge areas
        - Weekend vs weekday patterns

        Kigali-specific Analysis:
        - CBD (Kimihurura, Nyarugenge) patterns
        - Airport (Bugesera) traffic
        - University/school pickup trends
        - Market area (Kimironko) demand

        Used for:
        - Driver positioning recommendations
        - Service expansion decisions
        - Partnership with venues/businesses
        - Government urban planning support
        """,
        parameters=[
            OpenApiParameter(
                name='period',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Analysis period: 7days, 30days (default: 7days)',
                required=False
            ),
            OpenApiParameter(
                name='location_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Location type: pickup, dropoff, both (default: both)',
                required=False
            ),
            OpenApiParameter(
                name='top_n',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of hotspots to return (default: 10)',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get('period', '7days')
        location_type = request.query_params.get('location_type', 'both')
        top_n = int(request.query_params.get('top_n', 10))

        analytics = AnalyticsService.analyze_traffic_hotspots(period, location_type, top_n)

        return Response({
            'success': True,
            'period': period,
            'location_type': location_type,
            'traffic_analytics': analytics,
            'generated_at': timezone.now().isoformat()
        })


class UserBehaviorAnalyticsView(APIView):
    """
    GET /api/analytics/users/behavior/
    User behavior and engagement analytics
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        responses={200: UserBehaviorSerializer},
        summary="User behavior and engagement analytics (Privacy-compliant)",
        description="""
        Privacy-compliant user behavior analytics for product improvement:

        User Engagement Metrics:
        - New vs Returning users
        - User retention rate (Day 1, Day 7, Day 30)
        - Rides per user (frequency distribution)
        - Churn rate analysis

        Behavioral Patterns:
        - Preferred booking times
        - Average booking lead time
        - Cancellation patterns
        - Payment method preferences

        Cohort Analysis:
        - User acquisition cohorts
        - Cohort retention curves
        - Lifetime value estimation

        Privacy Compliance:
        - All data is aggregated and anonymized
        - No individual user identification
        - GDPR/Rwanda data protection compliant
        - Opt-out respected

        Used for:
        - Product feature prioritization
        - User retention campaigns
        - Onboarding optimization
        - Personalization strategies
        """,
        parameters=[
            OpenApiParameter(
                name='period',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Analysis period: 7days, 30days, 90days (default: 30days)',
                required=False
            ),
            OpenApiParameter(
                name='cohort',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Cohort to analyze (YYYY-MM format)',
                required=False
            )
        ]
    )
    def get(self, request):
        period = request.query_params.get('period', '30days')
        cohort = request.query_params.get('cohort')

        analytics = AnalyticsService.analyze_user_behavior(period, cohort)

        return Response({
            'success': True,
            'period': period,
            'user_behavior_analytics': analytics,
            'privacy_note': 'All data is aggregated and anonymized in compliance with Rwanda data protection laws',
            'generated_at': timezone.now().isoformat()
        })


class CustomReportGeneratorView(APIView):
    """
    POST /api/analytics/reports/generate/
    Generate custom analytics reports
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["Analytics & Business Intelligence"],
        request=CustomReportSerializer,
        responses={200: dict, 400: dict},
        summary="Generate custom analytics reports",
        description="""
        Generate custom analytics reports with flexible parameters:

        Report Types:
        - Executive Summary (high-level KPIs)
        - Operational Report (detailed metrics)
        - Financial Report (revenue breakdown)
        - Growth Report (trends and forecasts)
        - Regulatory Report (government compliance)

        Customization Options:
        - Date range selection
        - Metric selection
        - Geographic filtering
        - Export format (JSON, CSV, PDF)

        Scheduled Reports:
        - Daily automated reports
        - Weekly performance summaries
        - Monthly business reviews

        Used for:
        - Board presentations
        - Investor reporting
        - Government submissions
        - Internal team dashboards
        """,
        examples=[
            OpenApiExample(
                "Executive Summary Request",
                value={
                    "report_type": "executive_summary",
                    "period_start": "2025-09-01",
                    "period_end": "2025-09-30",
                    "metrics": ["total_rides", "revenue", "active_users", "driver_count"],
                    "format": "json"
                }
            )
        ]
    )
    def post(self, request):
        serializer = CustomReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AnalyticsService.generate_custom_report(
            report_type=serializer.validated_data['report_type'],
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end'],
            metrics=serializer.validated_data.get('metrics', []),
            filters=serializer.validated_data.get('filters', {}),
            user=request.user
        )

        if not result.get('success'):
            return Response(
                {'error': result.get('error', 'Report generation failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'success': True,
            'report': result['report'],
            'download_url': result.get('download_url'),
            'generated_at': timezone.now().isoformat()
        })
