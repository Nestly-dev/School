from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import (
    Count, Sum, Avg, Q, F,
    DecimalField, DurationField
)
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Ride, RideStatus, PaymentStatus

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """Only admin users can access reports"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


@extend_schema(
    tags=["Admin Reports"],
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Start date (YYYY-MM-DD)',
            required=False
        ),
        OpenApiParameter(
            name='end_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='End date (YYYY-MM-DD)',
            required=False
        ),
        OpenApiParameter(
            name='status',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Filter by ride status',
            required=False
        )
    ],
    responses={200: dict},
    summary="Administrative ride reports for RTDA",
    description="""
    Comprehensive ride statistics for government reporting:
    - Total rides by status
    - Revenue analysis
    - Geographic distribution
    - Time-based patterns
    - Compliance metrics
    """
)
class AdminRideReportsView(APIView):
    """GET /api/admin/reports/rides/"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Parse date filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        
        # Base queryset
        queryset = Ride.objects.all()
        
        # Apply filters
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Calculate statistics
        stats = queryset.aggregate(
            total_rides=Count('id'),
            completed_rides=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            cancelled_rides=Count('id', filter=Q(status=RideStatus.CANCELLED)),
            active_rides=Count('id', filter=Q(
                status__in=[
                    RideStatus.SEARCHING,
                    RideStatus.ACCEPTED,
                    RideStatus.DRIVER_ARRIVING,
                    RideStatus.ARRIVED,
                    RideStatus.ONGOING
                ]
            )),
            total_distance_km=Sum('distance_km'),
            total_revenue=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED)),
            avg_fare=Avg('final_fare', filter=Q(status=RideStatus.COMPLETED)),
            avg_distance_km=Avg('distance_km'),
        )
        
        # Rides by status breakdown
        status_breakdown = queryset.values('status').annotate(
            count=Count('id'),
            total_revenue=Sum('final_fare')
        ).order_by('-count')
        
        # Payment method breakdown
        payment_breakdown = queryset.filter(
            status=RideStatus.COMPLETED
        ).values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('final_fare')
        ).order_by('-count')
        
        # Daily ride trends (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_trends = queryset.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            rides_count=Count('id'),
            completed_count=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            revenue=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED))
        ).order_by('date')
        
        # Peak hours analysis
        peak_hours = queryset.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Top routes (by count)
        top_routes = queryset.filter(
            status=RideStatus.COMPLETED
        ).values(
            'pickup_address',
            'dropoff_address'
        ).annotate(
            count=Count('id'),
            avg_fare=Avg('final_fare'),
            avg_distance=Avg('distance_km')
        ).order_by('-count')[:20]
        
        # Cancellation analysis
        cancellations = queryset.filter(
            status=RideStatus.CANCELLED
        ).values('cancel_reason').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # RTDA compliance metrics
        reported_rides = queryset.filter(reported_to_rtda=True).count()
        unreported_completed = queryset.filter(
            status=RideStatus.COMPLETED,
            reported_to_rtda=False
        ).count()
        
        return Response({
            'summary': {
                'total_rides': stats['total_rides'] or 0,
                'completed_rides': stats['completed_rides'] or 0,
                'cancelled_rides': stats['cancelled_rides'] or 0,
                'active_rides': stats['active_rides'] or 0,
                'completion_rate': round(
                    (stats['completed_rides'] / stats['total_rides'] * 100)
                    if stats['total_rides'] else 0,
                    2
                ),
                'cancellation_rate': round(
                    (stats['cancelled_rides'] / stats['total_rides'] * 100)
                    if stats['total_rides'] else 0,
                    2
                ),
                'total_distance_km': float(stats['total_distance_km'] or 0),
                'total_revenue_rwf': float(stats['total_revenue'] or 0),
                'average_fare_rwf': float(stats['avg_fare'] or 0),
                'average_distance_km': float(stats['avg_distance_km'] or 0),
            },
            'status_breakdown': list(status_breakdown),
            'payment_breakdown': list(payment_breakdown),
            'daily_trends': list(daily_trends),
            'peak_hours': list(peak_hours),
            'top_routes': list(top_routes),
            'cancellation_reasons': list(cancellations),
            'compliance': {
                'reported_to_rtda': reported_rides,
                'unreported_completed': unreported_completed,
                'compliance_rate': round(
                    (reported_rides / (reported_rides + unreported_completed) * 100)
                    if (reported_rides + unreported_completed) else 100,
                    2
                )
            },
            'filters_applied': {
                'start_date': start_date,
                'end_date': end_date,
                'status': status_filter
            }
        })


@extend_schema(
    tags=["Admin Reports"],
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Start date (YYYY-MM-DD)',
            required=False
        ),
        OpenApiParameter(
            name='end_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='End date (YYYY-MM-DD)',
            required=False
        ),
        OpenApiParameter(
            name='min_rides',
            type=int,
            location=OpenApiParameter.QUERY,
            description='Minimum rides to include driver',
            required=False
        )
    ],
    responses={200: dict},
    summary="Driver performance reports",
    description="""
    Comprehensive driver statistics including:
    - Ride completion rates
    - Earnings and performance
    - Ratings and feedback
    - License verification status
    - Active/inactive drivers
    """
)
class AdminDriverReportsView(APIView):
    """GET /api/admin/reports/drivers/"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Parse filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        min_rides = int(request.query_params.get('min_rides', 0))
        
        # Base queryset for rides
        rides_qs = Ride.objects.all()
        if start_date:
            rides_qs = rides_qs.filter(created_at__gte=start_date)
        if end_date:
            rides_qs = rides_qs.filter(created_at__lte=end_date)
        
        # Get all drivers (users with driver_location)
        drivers = User.objects.filter(
            driver_location__isnull=False
        ).prefetch_related('driver_location')
        
        # Driver statistics
        driver_stats = rides_qs.values('driver').annotate(
            total_rides=Count('id'),
            completed_rides=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            cancelled_rides=Count('id', filter=Q(status=RideStatus.CANCELLED)),
            total_earnings=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED)),
            total_distance=Sum('distance_km', filter=Q(status=RideStatus.COMPLETED)),
            avg_rating=Avg('driver_rating'),
        ).filter(
            total_rides__gte=min_rides,
            driver__isnull=False
        ).order_by('-total_rides')
        
        # Enhance with driver details
        driver_reports = []
        for stat in driver_stats:
            try:
                driver = User.objects.get(id=stat['driver'])
                driver_location = getattr(driver, 'driver_location', None)
                
                completion_rate = 0
                if stat['total_rides'] > 0:
                    completion_rate = (stat['completed_rides'] / stat['total_rides']) * 100
                
                driver_reports.append({
                    'driver_id': driver.id,
                    'driver_name': f"{driver.first_name} {driver.last_name}".strip() or driver.username,
                    'email': driver.email,
                    'phone': getattr(driver, 'phone', None),
                    'is_online': driver_location.is_online if driver_location else False,
                    'total_rides': stat['total_rides'],
                    'completed_rides': stat['completed_rides'],
                    'cancelled_rides': stat['cancelled_rides'],
                    'completion_rate': round(completion_rate, 2),
                    'total_earnings_rwf': float(stat['total_earnings'] or 0),
                    'total_distance_km': float(stat['total_distance'] or 0),
                    'average_rating': round(float(stat['avg_rating'] or 0), 2),
                })
            except User.DoesNotExist:
                continue
        
        # Overall driver metrics
        total_drivers = drivers.count()
        active_drivers = drivers.filter(driver_location__is_online=True).count()
        drivers_with_rides = len(driver_reports)
        
        # Top performers
        top_earners = sorted(
            driver_reports,
            key=lambda x: x['total_earnings_rwf'],
            reverse=True
        )[:10]
        
        top_rated = sorted(
            [d for d in driver_reports if d['average_rating'] > 0],
            key=lambda x: (x['average_rating'], x['total_rides']),
            reverse=True
        )[:10]
        
        # License verification status (based on national_id presence)
        verified_drivers = drivers.filter(national_id__isnull=False).count()
        unverified_drivers = total_drivers - verified_drivers
        
        return Response({
            'summary': {
                'total_drivers': total_drivers,
                'active_drivers': active_drivers,
                'drivers_with_rides': drivers_with_rides,
                'verified_licenses': verified_drivers,
                'unverified_licenses': unverified_drivers,
                'verification_rate': round(
                    (verified_drivers / total_drivers * 100) if total_drivers else 0,
                    2
                )
            },
            'driver_details': driver_reports,
            'top_earners': top_earners,
            'top_rated': top_rated,
            'filters_applied': {
                'start_date': start_date,
                'end_date': end_date,
                'min_rides': min_rides
            }
        })


@extend_schema(
    tags=["Admin Reports"],
    responses={200: dict},
    summary="Real-time system dashboard",
    description="Real-time metrics for operational monitoring"
)
class SystemDashboardView(APIView):
    """GET /api/admin/dashboard/"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        
        # Today's stats
        today_rides = Ride.objects.filter(created_at__gte=today_start)
        today_stats = today_rides.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            active=Count('id', filter=Q(
                status__in=[
                    RideStatus.SEARCHING,
                    RideStatus.ACCEPTED,
                    RideStatus.DRIVER_ARRIVING,
                    RideStatus.ARRIVED,
                    RideStatus.ONGOING
                ]
            )),
            revenue=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED))
        )
        
        # Weekly comparison
        week_rides = Ride.objects.filter(created_at__gte=week_start)
        week_stats = week_rides.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            revenue=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED))
        )
        
        # Active users
        active_riders = Ride.objects.filter(
            created_at__gte=today_start
        ).values('rider').distinct().count()
        
        active_drivers = Ride.objects.filter(
            created_at__gte=today_start,
            driver__isnull=False
        ).values('driver').distinct().count()
        
        # Online drivers right now
        online_drivers = User.objects.filter(
            driver_location__is_online=True
        ).count()
        
        # Pending payments
        pending_payments = Ride.objects.filter(
            status=RideStatus.COMPLETED,
            payment_status=PaymentStatus.PENDING
        ).aggregate(
            count=Count('id'),
            amount=Sum('final_fare')
        )
        
        # System health indicators
        avg_wait_time = Ride.objects.filter(
            created_at__gte=today_start,
            accepted_at__isnull=False
        ).annotate(
            wait_time=F('accepted_at') - F('created_at')
        ).aggregate(
            avg_wait=Avg('wait_time')
        )
        
        return Response({
            'timestamp': now.isoformat(),
            'today': {
                'total_rides': today_stats['total'] or 0,
                'completed_rides': today_stats['completed'] or 0,
                'active_rides': today_stats['active'] or 0,
                'revenue_rwf': float(today_stats['revenue'] or 0),
                'active_riders': active_riders,
                'active_drivers': active_drivers
            },
            'this_week': {
                'total_rides': week_stats['total'] or 0,
                'completed_rides': week_stats['completed'] or 0,
                'revenue_rwf': float(week_stats['revenue'] or 0)
            },
            'current_status': {
                'online_drivers': online_drivers,
                'active_rides': today_stats['active'] or 0,
                'pending_payments_count': pending_payments['count'] or 0,
                'pending_payments_amount': float(pending_payments['amount'] or 0)
            },
            'performance': {
                'average_wait_time_seconds': (
                    avg_wait_time['avg_wait'].total_seconds()
                    if avg_wait_time['avg_wait'] else 0
                )
            }
        })


@extend_schema(
    tags=["Admin Reports"],
    request={'type': 'object', 'properties': {
        'ride_ids': {'type': 'array', 'items': {'type': 'integer'}},
        'all_completed': {'type': 'boolean'}
    }},
    responses={200: dict},
    summary="Mark rides as reported to RTDA",
    description="Bulk update rides for RTDA compliance reporting"
)
class MarkRTDAReportedView(APIView):
    """POST /api/admin/reports/rtda/mark-reported/"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        ride_ids = request.data.get('ride_ids', [])
        all_completed = request.data.get('all_completed', False)
        
        if all_completed:
            # Mark all unreported completed rides
            queryset = Ride.objects.filter(
                status=RideStatus.COMPLETED,
                reported_to_rtda=False
            )
        elif ride_ids:
            queryset = Ride.objects.filter(id__in=ride_ids)
        else:
            return Response(
                {'error': 'Provide ride_ids or set all_completed=true'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = queryset.update(
            reported_to_rtda=True,
            rtda_report_date=timezone.now()
        )
        
        return Response({
            'message': f'{updated_count} rides marked as reported to RTDA',
            'updated_count': updated_count
        })


@extend_schema(
    tags=["Admin Reports"],
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='Start date (YYYY-MM-DD)',
            required=True
        ),
        OpenApiParameter(
            name='end_date',
            type=str,
            location=OpenApiParameter.QUERY,
            description='End date (YYYY-MM-DD)',
            required=True
        )
    ],
    responses={200: dict},
    summary="Export data for RTDA compliance",
    description="Generate comprehensive report for Rwanda Transport Development Agency"
)
class RTDAComplianceExportView(APIView):
    """GET /api/admin/reports/rtda/export/"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all rides in date range
        rides = Ride.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).select_related('rider', 'driver').order_by('created_at')
        
        # Format for RTDA export
        ride_data = []
        for ride in rides:
            ride_data.append({
                'ride_id': ride.id,
                'date': ride.created_at.strftime('%Y-%m-%d'),
                'time': ride.created_at.strftime('%H:%M:%S'),
                'rider_id': ride.rider_id,
                'rider_phone': getattr(ride.rider, 'phone', ''),
                'driver_id': ride.driver_id if ride.driver else None,
                'driver_phone': getattr(ride.driver, 'phone', '') if ride.driver else '',
                'driver_license': getattr(ride.driver, 'national_id', '') if ride.driver else '',
                'pickup_location': ride.pickup_address,
                'dropoff_location': ride.dropoff_address,
                'distance_km': float(ride.distance_km or 0),
                'fare_rwf': float(ride.final_fare or ride.fare_estimate or 0),
                'status': ride.status,
                'payment_method': ride.payment_method,
                'payment_status': ride.payment_status,
                'payment_reference': ride.payment_reference,
                'completed_at': ride.completed_at.isoformat() if ride.completed_at else None,
            })
        
        # Summary statistics
        summary = rides.aggregate(
            total_rides=Count('id'),
            completed_rides=Count('id', filter=Q(status=RideStatus.COMPLETED)),
            total_revenue=Sum('final_fare', filter=Q(status=RideStatus.COMPLETED)),
            total_distance=Sum('distance_km', filter=Q(status=RideStatus.COMPLETED)),
        )
        
        return Response({
            'report_metadata': {
                'generated_at': timezone.now().isoformat(),
                'start_date': start_date,
                'end_date': end_date,
                'total_records': len(ride_data)
            },
            'summary': {
                'total_rides': summary['total_rides'] or 0,
                'completed_rides': summary['completed_rides'] or 0,
                'total_revenue_rwf': float(summary['total_revenue'] or 0),
                'total_distance_km': float(summary['total_distance'] or 0)
            },
            'rides': ride_data
        })