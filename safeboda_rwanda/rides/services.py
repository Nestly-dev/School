"""
Booking and Real-Time Tracking Services for SafeBoda Rwanda
Integrates with location services, caching, and notifications
"""
from typing import Optional, List, Dict, Any, NamedTuple
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
import logging

from .models import Ride, RideStatus, RideTracking, Notification, PaymentStatus
from locations.services import LocationService

User = get_user_model()
logger = logging.getLogger(__name__)


class BookingResult(NamedTuple):
    """Result from booking service operations"""
    success: bool
    ride: Optional[Ride] = None
    nearby_drivers: List[Dict[str, Any]] = []
    error: Optional[str] = None
    reference: Optional[str] = None


class BookingService:
    """
    Integrated booking service combining:
    - Location services (geocoding, routing)
    - Driver matching
    - Fare calculation
    - Notification system
    """

    # Rwanda-specific pricing (in RWF)
    BASE_FARE = Decimal("500")
    PER_KM_RATE = Decimal("800")
    SEARCH_RADIUS_KM = 5.0

    @classmethod
    def create_booking(
        cls,
        rider: User,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float,
        payment_method: str = 'MTN_MOMO'
    ) -> BookingResult:
        """
        Create a new ride booking with integrated services:
        1. Geocode pickup/dropoff addresses
        2. Calculate route and distance
        3. Estimate fare
        4. Find nearby drivers
        5. Create ride record
        6. Send notifications to nearby drivers
        """
        try:
            # 1. Geocode addresses (async in background, use defaults if slow)
            pickup_address = LocationService.reverse_geocode(pickup_lat, pickup_lng) or "Pickup Location"
            dropoff_address = LocationService.reverse_geocode(dropoff_lat, dropoff_lng) or "Dropoff Location"

            # 2. Calculate route
            route_data = LocationService.calculate_route(
                pickup_lat, pickup_lng,
                dropoff_lat, dropoff_lng
            )

            distance_km = Decimal(str(route_data.get('distance_km', 0)))

            # 3. Calculate fare
            fare_estimate = cls.calculate_fare(distance_km)

            # 4. Find nearby available drivers
            nearby_drivers = cls.find_nearby_drivers(pickup_lat, pickup_lng)

            # 5. Create ride record
            with transaction.atomic():
                ride = Ride.objects.create(
                    rider=rider,
                    pickup_lat=Decimal(str(pickup_lat)),
                    pickup_lng=Decimal(str(pickup_lng)),
                    dropoff_lat=Decimal(str(dropoff_lat)),
                    dropoff_lng=Decimal(str(dropoff_lng)),
                    pickup_address=pickup_address,
                    dropoff_address=dropoff_address,
                    distance_km=distance_km,
                    fare_estimate=fare_estimate,
                    payment_method=payment_method,
                    status=RideStatus.SEARCHING
                )

                # 6. Send notifications to nearby drivers
                cls._notify_nearby_drivers(ride, nearby_drivers)

                # 7. Cache ride for quick access
                cache.set(f'ride:{ride.id}', ride, timeout=3600)

            logger.info(f"Booking created: Ride #{ride.id} for rider {rider.id}")

            return BookingResult(
                success=True,
                ride=ride,
                nearby_drivers=nearby_drivers
            )

        except Exception as e:
            logger.error(f"Booking creation failed: {str(e)}")
            return BookingResult(
                success=False,
                error=f"Failed to create booking: {str(e)}"
            )

    @classmethod
    def accept_ride(cls, ride: Ride, driver: User) -> bool:
        """Driver accepts a ride request"""
        try:
            if ride.status != RideStatus.SEARCHING:
                return False

            with transaction.atomic():
                ride.driver = driver
                ride.update_status(RideStatus.ACCEPTED)
                ride.status = RideStatus.DRIVER_ARRIVING
                ride.accepted_at = timezone.now()
                ride.save()

                # Notify rider
                Notification.objects.create(
                    user=ride.rider,
                    ride=ride,
                    notification_type=Notification.NotificationType.RIDE_ACCEPTED,
                    title="Driver Found!",
                    message=f"Your driver is on the way. ETA: 5-10 minutes."
                )

                # Update cache
                cache.set(f'ride:{ride.id}', ride, timeout=3600)

            logger.info(f"Ride #{ride.id} accepted by driver {driver.id}")
            return True

        except Exception as e:
            logger.error(f"Accept ride failed: {str(e)}")
            return False

    @classmethod
    def start_ride(cls, ride: Ride, driver: User) -> bool:
        """Driver starts the ride"""
        try:
            if ride.driver != driver or ride.status != RideStatus.ARRIVED:
                return False

            with transaction.atomic():
                ride.update_status(RideStatus.ONGOING)
                ride.started_at = timezone.now()
                ride.save()

                # Notify rider
                Notification.objects.create(
                    user=ride.rider,
                    ride=ride,
                    notification_type=Notification.NotificationType.RIDE_STARTED,
                    title="Ride Started",
                    message="Your ride has started. Enjoy your trip!"
                )

            logger.info(f"Ride #{ride.id} started")
            return True

        except Exception as e:
            logger.error(f"Start ride failed: {str(e)}")
            return False

    @classmethod
    def complete_ride(cls, ride: Ride, driver: User) -> bool:
        """Driver completes the ride"""
        try:
            if ride.driver != driver or ride.status != RideStatus.ONGOING:
                return False

            with transaction.atomic():
                # Calculate final fare based on actual distance
                if ride.distance_km:
                    ride.final_fare = cls.calculate_fare(ride.distance_km)
                else:
                    ride.final_fare = ride.fare_estimate

                ride.update_status(RideStatus.COMPLETED)
                ride.completed_at = timezone.now()
                ride.save()

                # Notify rider
                Notification.objects.create(
                    user=ride.rider,
                    ride=ride,
                    notification_type=Notification.NotificationType.RIDE_COMPLETED,
                    title="Ride Completed",
                    message=f"Your ride is complete. Fare: {ride.final_fare} RWF"
                )

            logger.info(f"Ride #{ride.id} completed")
            return True

        except Exception as e:
            logger.error(f"Complete ride failed: {str(e)}")
            return False

    @classmethod
    def cancel_ride(cls, ride: Ride, user: User, reason: str = "") -> bool:
        """Cancel a ride (by rider or driver)"""
        try:
            # Can only cancel if not completed
            if ride.status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
                return False

            with transaction.atomic():
                ride.cancel_reason = reason
                ride.cancelled_by = user
                ride.update_status(RideStatus.CANCELLED)
                ride.cancelled_at = timezone.now()
                ride.save()

                # Notify the other party
                other_user = ride.driver if user == ride.rider else ride.rider
                if other_user:
                    Notification.objects.create(
                        user=other_user,
                        ride=ride,
                        notification_type=Notification.NotificationType.RIDE_CANCELLED,
                        title="Ride Cancelled",
                        message=f"Ride has been cancelled. Reason: {reason or 'Not specified'}"
                    )

                # Clear cache
                cache.delete(f'ride:{ride.id}')

            logger.info(f"Ride #{ride.id} cancelled by user {user.id}")
            return True

        except Exception as e:
            logger.error(f"Cancel ride failed: {str(e)}")
            return False

    @classmethod
    def process_payment(cls, ride: Ride, phone_number: str) -> BookingResult:
        """
        Process payment via Rwanda mobile money
        This is a design/simulation - real implementation would integrate with:
        - MTN Mobile Money API
        - Airtel Money API
        """
        try:
            # Detect provider from phone number
            provider = cls._detect_mobile_money_provider(phone_number)

            amount = float(ride.final_fare or ride.fare_estimate)

            # Generate transaction reference
            reference = f"SB{ride.id}{timezone.now().strftime('%Y%m%d%H%M%S')}"

            # Simulate payment processing
            # In production, this would call actual mobile money APIs
            with transaction.atomic():
                ride.payment_status = PaymentStatus.PROCESSING
                ride.payment_reference = reference
                ride.save()

                # Simulate successful payment
                ride.payment_status = PaymentStatus.COMPLETED
                ride.save()

                # Notify rider
                Notification.objects.create(
                    user=ride.rider,
                    ride=ride,
                    notification_type=Notification.NotificationType.PAYMENT_SUCCESS,
                    title="Payment Successful",
                    message=f"Payment of {amount} RWF via {provider} completed. Ref: {reference}"
                )

            logger.info(f"Payment processed for Ride #{ride.id}: {reference}")

            return BookingResult(
                success=True,
                ride=ride,
                reference=reference
            )

        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")

            # Update payment status
            ride.payment_status = PaymentStatus.FAILED
            ride.save()

            return BookingResult(
                success=False,
                error=f"Payment failed: {str(e)}"
            )

    @staticmethod
    def calculate_fare(distance_km: Decimal) -> Decimal:
        """Calculate fare based on Rwanda pricing model"""
        return Ride.price_for(
            distance_km,
            base=BookingService.BASE_FARE,
            per_km=BookingService.PER_KM_RATE
        )

    @staticmethod
    def find_nearby_drivers(lat: float, lng: float, radius_km: float = None) -> List[Dict[str, Any]]:
        """
        Find nearby available drivers using location service
        Returns list of driver info with distance
        """
        if radius_km is None:
            radius_km = BookingService.SEARCH_RADIUS_KM

        try:
            # Get available drivers from cache or database
            available_drivers = User.objects.filter(
                is_active=True,
                # Assuming you have a user profile with driver status
            ).values_list('id', flat=True)[:20]

            # Use location service to find nearby
            nearby = []
            for driver_id in available_drivers:
                # In production, get actual driver locations from cache/tracking
                driver_lat = lat + 0.01  # Simulated
                driver_lng = lng + 0.01  # Simulated

                distance = LocationService.calculate_distance(
                    lat, lng, driver_lat, driver_lng
                )

                if distance <= radius_km:
                    nearby.append({
                        'driver_id': driver_id,
                        'distance_km': round(distance, 2),
                        'eta_minutes': int(distance / 0.5)  # Assume 30 km/h avg speed
                    })

            # Sort by distance
            nearby.sort(key=lambda x: x['distance_km'])

            return nearby[:10]  # Return top 10

        except Exception as e:
            logger.error(f"Find nearby drivers failed: {str(e)}")
            return []

    @staticmethod
    def _notify_nearby_drivers(ride: Ride, nearby_drivers: List[Dict[str, Any]]):
        """Send ride request notifications to nearby drivers"""
        notifications = []
        for driver_info in nearby_drivers[:5]:  # Notify top 5 drivers
            notifications.append(
                Notification(
                    user_id=driver_info['driver_id'],
                    ride=ride,
                    notification_type=Notification.NotificationType.RIDE_REQUEST,
                    title="New Ride Request",
                    message=f"New ride request {driver_info['distance_km']}km away. "
                           f"Fare estimate: {ride.fare_estimate} RWF"
                )
            )

        if notifications:
            Notification.objects.bulk_create(notifications)

    @staticmethod
    def _detect_mobile_money_provider(phone_number: str) -> str:
        """Detect mobile money provider from Rwanda phone number"""
        # Rwanda phone format: +250 7X XXX XXXX
        cleaned = phone_number.replace('+', '').replace(' ', '')

        if '25078' in cleaned or cleaned.startswith('078'):
            return 'MTN_MOMO'
        elif '25073' in cleaned or cleaned.startswith('073'):
            return 'AIRTEL_MONEY'
        else:
            return 'UNKNOWN'


class RealTimeTrackingService:
    """
    Real-time location tracking service for active rides
    Uses caching for fast location updates
    """

    CACHE_TIMEOUT = 30  # seconds

    @classmethod
    def update_driver_location(
        cls,
        ride: Ride,
        lat: float,
        lng: float,
        speed_kmh: float = 0,
        heading: Optional[float] = None
    ) -> bool:
        """
        Update driver's current location during active ride
        Stores in cache for fast retrieval and database for history
        """
        try:
            # Only track active rides
            if not ride.is_active():
                return False

            # Update ride's current location
            with transaction.atomic():
                ride.current_lat = Decimal(str(lat))
                ride.current_lng = Decimal(str(lng))
                ride.save(update_fields=['current_lat', 'current_lng', 'updated_at'])

                # Create tracking point for history
                RideTracking.objects.create(
                    ride=ride,
                    lat=Decimal(str(lat)),
                    lng=Decimal(str(lng)),
                    speed_kmh=speed_kmh,
                    heading=heading
                )

            # Update cache for fast retrieval
            location_data = {
                'lat': lat,
                'lng': lng,
                'speed_kmh': speed_kmh,
                'heading': heading,
                'timestamp': timezone.now().isoformat()
            }
            cache.set(
                f'ride_location:{ride.id}',
                location_data,
                timeout=cls.CACHE_TIMEOUT
            )

            # Check if driver is near pickup (notify rider)
            if ride.status == RideStatus.DRIVER_ARRIVING:
                distance_to_pickup = LocationService.calculate_distance(
                    float(lat), float(lng),
                    float(ride.pickup_lat), float(ride.pickup_lng)
                )

                if distance_to_pickup <= 0.1:  # Within 100m
                    cls._notify_driver_nearby(ride)

            return True

        except Exception as e:
            logger.error(f"Update location failed: {str(e)}")
            return False

    @classmethod
    def get_current_location(cls, booking_id: int) -> Optional[Dict[str, Any]]:
        """Get current driver location from cache or database"""
        try:
            # Try cache first
            location = cache.get(f'ride_location:{booking_id}')
            if location:
                return location

            # Fallback to database
            ride = Ride.objects.get(pk=booking_id)
            if ride.current_lat and ride.current_lng:
                return {
                    'lat': float(ride.current_lat),
                    'lng': float(ride.current_lng),
                    'timestamp': ride.updated_at.isoformat()
                }

            # Get latest tracking point
            latest_track = ride.tracking_points.first()
            if latest_track:
                return {
                    'lat': float(latest_track.lat),
                    'lng': float(latest_track.lng),
                    'speed_kmh': latest_track.speed_kmh,
                    'heading': latest_track.heading,
                    'timestamp': latest_track.timestamp.isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Get current location failed: {str(e)}")
            return None

    @classmethod
    def get_route_history(cls, booking_id: int) -> List[Dict[str, Any]]:
        """Get full route history for a ride"""
        try:
            tracking_points = RideTracking.objects.filter(
                ride_id=booking_id
            ).order_by('timestamp')

            return [
                {
                    'lat': float(point.lat),
                    'lng': float(point.lng),
                    'speed_kmh': point.speed_kmh,
                    'heading': point.heading,
                    'timestamp': point.timestamp.isoformat()
                }
                for point in tracking_points
            ]

        except Exception as e:
            logger.error(f"Get route history failed: {str(e)}")
            return []

    @staticmethod
    def _notify_driver_nearby(ride: Ride):
        """Notify rider when driver is nearby"""
        # Check if already notified (avoid spam)
        recent_notification = Notification.objects.filter(
            ride=ride,
            notification_type=Notification.NotificationType.DRIVER_NEARBY,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).exists()

        if not recent_notification:
            Notification.objects.create(
                user=ride.rider,
                ride=ride,
                notification_type=Notification.NotificationType.DRIVER_NEARBY,
                title="Driver Nearby",
                message="Your driver is almost at the pickup location!"
            )
