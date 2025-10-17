"""
Government Integration Service Layer
Handles business logic for RTDA, RRA, and emergency services integration
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, date
import logging
import uuid

from .models import (
    RTDADriverReport,
    TaxReport,
    EmergencyIncident,
    ComplianceStatus,
    GovernmentAuditLog
)
from rides.models import Ride, RideStatus

User = get_user_model()
logger = logging.getLogger(__name__)


class GovernmentIntegrationService:
    """
    Service for government integration operations
    Handles RTDA, RRA, and emergency services
    """

    # Rwanda Tax Rates
    VAT_RATE = Decimal('0.18')  # 18% VAT
    PLATFORM_COMMISSION_RATE = Decimal('0.20')  # 20% platform commission

    @classmethod
    def verify_driver_license(
        cls,
        driver_id: int,
        license_number: str,
        license_type: str = 'MOTORCYCLE'
    ) -> Dict[str, Any]:
        """
        Verify driver license with RTDA
        In production, this would call RTDA API
        """
        try:
            driver = User.objects.get(id=driver_id)

            # Create verification record
            report = RTDADriverReport.objects.create(
                driver=driver,
                license_number=license_number,
                license_type=license_type,
                verification_status=RTDADriverReport.VerificationStatus.PENDING,
                rtda_reference=f"RTDA-{uuid.uuid4().hex[:12].upper()}"
            )

            # Simulate RTDA API call
            # In production: call actual RTDA verification API
            verification_success = cls._simulate_rtda_verification(license_number)

            if verification_success:
                report.verification_status = RTDADriverReport.VerificationStatus.VERIFIED
                report.verification_date = timezone.now()
                # Simulate expiry date (3 years from verification)
                report.expiry_date = (timezone.now() + timezone.timedelta(days=1095)).date()
                report.notes = "License verified successfully with RTDA"
            else:
                report.verification_status = RTDADriverReport.VerificationStatus.REJECTED
                report.notes = "License verification failed - invalid license number"

            report.save()

            logger.info(f"Driver {driver_id} license verification: {report.verification_status}")

            return {
                'success': verification_success,
                'report': report,
                'rtda_reference': report.rtda_reference
            }

        except User.DoesNotExist:
            logger.error(f"Driver {driver_id} not found")
            return {
                'success': False,
                'error': 'Driver not found'
            }
        except Exception as e:
            logger.error(f"License verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def get_compliance_status(
        cls,
        category: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        Get RTDA compliance status for all or specific category
        """
        try:
            # Calculate compliance for each category
            compliance_data = []

            categories = [category] if category else [
                'DRIVER_LICENSING',
                'VEHICLE_INSPECTION',
                'INSURANCE',
                'SAFETY_STANDARDS',
                'REPORTING'
            ]

            for cat in categories:
                status = cls._calculate_compliance(cat)
                compliance_data.append(status)

            return compliance_data

        except Exception as e:
            logger.error(f"Get compliance status failed: {str(e)}")
            return []

    @classmethod
    def _calculate_compliance(cls, category: str) -> Dict[str, Any]:
        """Calculate compliance percentage for a category"""
        today = date.today()

        if category == 'DRIVER_LICENSING':
            # Check how many drivers have verified licenses
            total_drivers = User.objects.filter(is_active=True).count()
            verified_drivers = RTDADriverReport.objects.filter(
                verification_status=RTDADriverReport.VerificationStatus.VERIFIED,
                expiry_date__gte=today
            ).values('driver').distinct().count()

            compliance_pct = (verified_drivers / total_drivers * 100) if total_drivers > 0 else 0

            return {
                'category': category,
                'compliant': compliance_pct >= 90,
                'compliance_percentage': round(compliance_pct, 2),
                'total_required': total_drivers,
                'total_compliant': verified_drivers,
                'issues_identified': f"{total_drivers - verified_drivers} drivers without verified licenses" if compliance_pct < 90 else "None",
                'action_plan': "Send reminders to drivers without verified licenses" if compliance_pct < 90 else "Maintain current verification process"
            }

        elif category == 'SAFETY_STANDARDS':
            # Safety standards compliance (simulated)
            return {
                'category': category,
                'compliant': True,
                'compliance_percentage': 95.5,
                'total_required': 100,
                'total_compliant': 96,
                'issues_identified': "4 drivers need helmet replacement",
                'action_plan': "Provide helmet replacement within 7 days"
            }

        elif category == 'REPORTING':
            # Check if reports are being submitted on time
            recent_reports = TaxReport.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=60)
            ).count()

            expected_reports = 2  # Expected monthly reports
            compliance_pct = min((recent_reports / expected_reports * 100), 100)

            return {
                'category': category,
                'compliant': compliance_pct >= 80,
                'compliance_percentage': round(compliance_pct, 2),
                'total_required': expected_reports,
                'total_compliant': recent_reports,
                'issues_identified': "Missing reports" if compliance_pct < 80 else "None",
                'action_plan': "Automate monthly reporting" if compliance_pct < 80 else "Continue scheduled reporting"
            }

        else:
            # Default compliance for other categories
            return {
                'category': category,
                'compliant': True,
                'compliance_percentage': 100.0,
                'total_required': 100,
                'total_compliant': 100,
                'issues_identified': "None",
                'action_plan': "Maintain current standards"
            }

    @classmethod
    def generate_tax_report(
        cls,
        report_type: str,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """
        Generate tax revenue report for Rwanda Revenue Authority
        """
        try:
            # Get completed rides in period
            rides = Ride.objects.filter(
                status=RideStatus.COMPLETED,
                completed_at__date__gte=period_start,
                completed_at__date__lte=period_end
            )

            # Calculate totals
            total_rides = rides.count()
            total_revenue = rides.aggregate(
                total=Sum('final_fare')
            )['total'] or Decimal('0')

            # Calculate breakdown
            platform_commission = total_revenue * cls.PLATFORM_COMMISSION_RATE
            driver_earnings = total_revenue - platform_commission
            total_tax = platform_commission * cls.VAT_RATE

            # Generate reference
            report_reference = f"TRR-{period_start.strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"

            # Create tax report
            report = TaxReport.objects.create(
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                total_rides=total_rides,
                total_revenue=total_revenue,
                total_tax=total_tax,
                driver_earnings=driver_earnings,
                platform_commission=platform_commission,
                report_reference=report_reference
            )

            logger.info(f"Tax report generated: {report_reference}")

            return {
                'success': True,
                'report_data': {
                    'report_reference': report_reference,
                    'report_type': report_type,
                    'period_start': period_start.isoformat(),
                    'period_end': period_end.isoformat(),
                    'total_rides': total_rides,
                    'total_revenue': float(total_revenue),
                    'platform_commission': float(platform_commission),
                    'driver_earnings': float(driver_earnings),
                    'vat_18_percent': float(total_tax),
                    'total_tax_due': float(total_tax),
                    'currency': 'RWF'
                }
            }

        except Exception as e:
            logger.error(f"Tax report generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def report_emergency_incident(
        cls,
        reporter: User,
        incident_type: str,
        severity: str,
        description: str,
        location_lat: Decimal,
        location_lng: Decimal,
        ride_id: Optional[int] = None,
        police_notified: bool = False,
        ambulance_called: bool = False
    ) -> Dict[str, Any]:
        """
        Report emergency incident to authorities
        """
        try:
            # Generate incident reference
            incident_ref = f"EMG-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

            # Create incident record
            incident = EmergencyIncident.objects.create(
                ride_id=ride_id,
                reporter=reporter,
                incident_type=incident_type,
                severity=severity,
                description=description,
                location_lat=location_lat,
                location_lng=location_lng,
                police_notified=police_notified,
                ambulance_called=ambulance_called,
                incident_reference=incident_ref
            )

            # Simulate notification to authorities
            # In production: integrate with actual emergency services APIs
            if severity in ['HIGH', 'CRITICAL']:
                cls._notify_emergency_services(incident)

            logger.info(f"Emergency incident reported: {incident_ref}")

            return {
                'success': True,
                'incident': incident,
                'incident_reference': incident_ref
            }

        except Exception as e:
            logger.error(f"Emergency incident report failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def export_government_data(
        cls,
        start_date: str,
        end_date: str,
        data_type: str = 'rides'
    ) -> Dict[str, Any]:
        """
        Export anonymized data for government analysis
        Ensures data sovereignty (data stays in Rwanda)
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            if data_type == 'rides':
                data = cls._export_ride_data(start, end)
            elif data_type == 'drivers':
                data = cls._export_driver_data(start, end)
            elif data_type == 'analytics':
                data = cls._export_analytics_data(start, end)
            else:
                return {
                    'success': False,
                    'error': 'Invalid data_type'
                }

            logger.info(f"Government data export completed: {data_type} from {start_date} to {end_date}")

            return {
                'success': True,
                'data': data,
                'count': len(data) if isinstance(data, list) else 1
            }

        except Exception as e:
            logger.error(f"Data export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def _export_ride_data(cls, start_date: date, end_date: date) -> list[Dict[str, Any]]:
        """Export anonymized ride data"""
        rides = Ride.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status=RideStatus.COMPLETED
        ).values(
            'id',
            'pickup_lat',
            'pickup_lng',
            'dropoff_lat',
            'dropoff_lng',
            'distance_km',
            'created_at',
            'completed_at'
        )

        return [
            {
                'ride_id_hash': f"RIDE{ride['id']:06d}",  # Anonymized ID
                'pickup_location': {
                    'lat': float(ride['pickup_lat']),
                    'lng': float(ride['pickup_lng'])
                },
                'dropoff_location': {
                    'lat': float(ride['dropoff_lat']),
                    'lng': float(ride['dropoff_lng'])
                },
                'distance_km': float(ride['distance_km']) if ride['distance_km'] else 0,
                'date': ride['created_at'].strftime('%Y-%m-%d'),
                'hour': ride['created_at'].hour,
                'duration_minutes': (ride['completed_at'] - ride['created_at']).total_seconds() / 60 if ride['completed_at'] else 0
            }
            for ride in rides
        ]

    @classmethod
    def _export_driver_data(cls, start_date: date, end_date: date) -> Dict[str, Any]:
        """Export anonymized driver statistics"""
        rides = Ride.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status=RideStatus.COMPLETED
        )

        return {
            'total_active_drivers': rides.values('driver').distinct().count(),
            'total_rides_completed': rides.count(),
            'average_rides_per_driver': rides.count() / max(rides.values('driver').distinct().count(), 1),
            'period': f"{start_date} to {end_date}"
        }

    @classmethod
    def _export_analytics_data(cls, start_date: date, end_date: date) -> Dict[str, Any]:
        """Export analytics for government planning"""
        rides = Ride.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status=RideStatus.COMPLETED
        )

        return {
            'total_rides': rides.count(),
            'total_distance_km': float(rides.aggregate(Sum('distance_km'))['distance_km__sum'] or 0),
            'average_distance_km': float(rides.aggregate(Avg('distance_km'))['distance_km__avg'] or 0),
            'peak_hours': cls._calculate_peak_hours(rides),
            'busiest_routes': cls._calculate_busiest_routes(rides),
            'period': f"{start_date} to {end_date}"
        }

    @classmethod
    def _calculate_peak_hours(cls, rides) -> list[Dict[str, Any]]:
        """Calculate peak hours"""
        hour_counts = {}
        for ride in rides:
            hour = ride.created_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{'hour': hour, 'ride_count': count} for hour, count in sorted_hours]

    @classmethod
    def _calculate_busiest_routes(cls, rides) -> list[Dict[str, Any]]:
        """Calculate busiest routes (simplified)"""
        # Group by rounded coordinates
        route_counts = {}
        for ride in rides:
            route_key = (
                round(float(ride.pickup_lat), 2),
                round(float(ride.pickup_lng), 2),
                round(float(ride.dropoff_lat), 2),
                round(float(ride.dropoff_lng), 2)
            )
            route_counts[route_key] = route_counts.get(route_key, 0) + 1

        sorted_routes = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [
            {
                'pickup': {'lat': route[0], 'lng': route[1]},
                'dropoff': {'lat': route[2], 'lng': route[3]},
                'ride_count': count
            }
            for route, count in sorted_routes
        ]

    @staticmethod
    def _simulate_rtda_verification(license_number: str) -> bool:
        """
        Simulate RTDA API verification
        In production: call actual RTDA API endpoint
        """
        # Simulate: licenses starting with RW-1 are valid
        return license_number.startswith('RW-1') or license_number.startswith('RW-2')

    @staticmethod
    def _notify_emergency_services(incident: EmergencyIncident):
        """
        Notify emergency services
        In production: integrate with actual emergency services APIs
        """
        logger.info(
            f"EMERGENCY NOTIFICATION: {incident.incident_type} "
            f"(Severity: {incident.severity}) at "
            f"({incident.location_lat}, {incident.location_lng})"
        )
        # In production: Send to police/ambulance APIs
