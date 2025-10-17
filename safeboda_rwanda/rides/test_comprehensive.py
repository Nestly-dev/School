"""
Comprehensive Test Suite for Rides App
Covers unit tests, integration tests, and API endpoint tests
"""
import pytest
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Ride, RideStatus, RideTracking, Notification, PaymentStatus
from .services import BookingService, RealTimeTrackingService

User = get_user_model()


class RideModelTests(TestCase):
    """Unit tests for Ride model"""

    def setUp(self):
        self.rider = User.objects.create_user(
            email='rider@test.com',
            password='testpass123',
            phone_number='+250788123456'
        )
        self.driver = User.objects.create_user(
            email='driver@test.com',
            password='testpass123',
            phone_number='+250788654321'
        )

    def test_ride_creation(self):
        """Test creating a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )

        self.assertEqual(ride.status, RideStatus.REQUESTED)
        self.assertEqual(ride.rider, self.rider)
        self.assertIsNone(ride.driver)

    def test_fare_calculation(self):
        """Test fare calculation with Rwanda pricing"""
        distance = Decimal('10.0')
        fare = Ride.price_for(distance)

        expected = Decimal('500') + (Decimal('800') * distance)  # 8500 RWF
        self.assertEqual(fare, expected)

    def test_ride_status_update(self):
        """Test ride status transitions"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            distance_km=Decimal('5.0')
        )

        # Test status transition to ACCEPTED
        ride.driver = self.driver
        ride.update_status(RideStatus.ACCEPTED, user=self.driver)
        self.assertEqual(ride.status, RideStatus.ACCEPTED)
        self.assertIsNotNone(ride.accepted_at)

        # Test status transition to ONGOING
        ride.update_status(RideStatus.ONGOING, user=self.driver)
        self.assertEqual(ride.status, RideStatus.ONGOING)
        self.assertIsNotNone(ride.started_at)

        # Test status transition to COMPLETED
        ride.update_status(RideStatus.COMPLETED, user=self.driver)
        self.assertEqual(ride.status, RideStatus.COMPLETED)
        self.assertIsNotNone(ride.completed_at)
        self.assertIsNotNone(ride.final_fare)

    def test_ride_duration_calculation(self):
        """Test ride duration calculation"""
        ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            distance_km=Decimal('5.0')
        )

        ride.started_at = timezone.now()
        ride.completed_at = timezone.now() + timezone.timedelta(minutes=20)
        ride.save()

        duration = ride.calculate_duration_minutes()
        self.assertEqual(duration, 20)

    def test_is_active(self):
        """Test is_active method"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
        )

        ride.status = RideStatus.ONGOING
        self.assertTrue(ride.is_active())

        ride.status = RideStatus.COMPLETED
        self.assertFalse(ride.is_active())


class BookingServiceTests(TransactionTestCase):
    """Unit tests for BookingService"""

    def setUp(self):
        self.rider = User.objects.create_user(
            email='rider@test.com',
            password='testpass123',
            phone_number='+250788123456'
        )
        self.driver = User.objects.create_user(
            email='driver@test.com',
            password='testpass123',
            phone_number='+250788654321'
        )

    def test_create_booking_success(self):
        """Test successful booking creation"""
        result = BookingService.create_booking(
            rider=self.rider,
            pickup_lat=-1.9536,
            pickup_lng=30.0606,
            dropoff_lat=-1.9442,
            dropoff_lng=30.0619,
            payment_method='MTN_MOMO'
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.ride)
        self.assertEqual(result.ride.rider, self.rider)
        self.assertEqual(result.ride.payment_method, 'MTN_MOMO')

    def test_accept_ride(self):
        """Test driver accepting a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.SEARCHING
        )

        success = BookingService.accept_ride(ride, self.driver)

        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.driver, self.driver)
        self.assertEqual(ride.status, RideStatus.DRIVER_ARRIVING)

    def test_complete_ride(self):
        """Test completing a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            distance_km=Decimal('5.0'),
            status=RideStatus.ONGOING
        )

        success = BookingService.complete_ride(ride, self.driver)

        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.status, RideStatus.COMPLETED)
        self.assertIsNotNone(ride.final_fare)

    def test_cancel_ride(self):
        """Test cancelling a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.SEARCHING
        )

        success = BookingService.cancel_ride(ride, self.rider, reason="Changed plans")

        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.status, RideStatus.CANCELLED)
        self.assertEqual(ride.cancel_reason, "Changed plans")


class RidesAPITests(APITestCase):
    """API endpoint tests for rides"""

    def setUp(self):
        self.client = APIClient()
        self.rider = User.objects.create_user(
            email='rider@test.com',
            password='testpass123',
            phone_number='+250788123456'
        )
        self.driver = User.objects.create_user(
            email='driver@test.com',
            password='testpass123',
            phone_number='+250788654321'
        )

    def test_create_booking_endpoint(self):
        """Test POST /api/bookings/create/"""
        self.client.force_authenticate(user=self.rider)

        data = {
            'pickup_lat': -1.9536,
            'pickup_lng': 30.0606,
            'dropoff_lat': -1.9442,
            'dropoff_lng': 30.0619,
            'payment_method': 'MTN_MOMO'
        }

        response = self.client.post('/api/rides/bookings/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('booking', response.data)
        self.assertEqual(response.data['booking']['payment_method'], 'MTN_MOMO')

    def test_create_booking_unauthenticated(self):
        """Test booking creation fails without authentication"""
        data = {
            'pickup_lat': -1.9536,
            'pickup_lng': 30.0606,
            'dropoff_lat': -1.9442,
            'dropoff_lng': 30.0619
        }

        response = self.client.post('/api/rides/bookings/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_booking_detail(self):
        """Test GET /api/bookings/{id}/"""
        self.client.force_authenticate(user=self.rider)

        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619')
        )

        response = self.client.get(f'/api/rides/bookings/{ride.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], ride.id)

    def test_get_active_bookings(self):
        """Test GET /api/bookings/active/"""
        self.client.force_authenticate(user=self.rider)

        # Create active rides
        Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.SEARCHING
        )
        Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.COMPLETED
        )

        response = self.client.get('/api/rides/bookings/active/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only active ride

    def test_cancel_booking(self):
        """Test POST /api/bookings/{id}/cancel/"""
        self.client.force_authenticate(user=self.rider)

        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.SEARCHING
        )

        data = {'reason': 'Found another ride'}
        response = self.client.post(f'/api/rides/bookings/{ride.id}/cancel/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ride.refresh_from_db()
        self.assertEqual(ride.status, RideStatus.CANCELLED)


class RealTimeTrackingTests(TestCase):
    """Tests for real-time tracking service"""

    def setUp(self):
        self.rider = User.objects.create_user(
            email='rider@test.com',
            password='testpass123',
            phone_number='+250788123456'
        )
        self.driver = User.objects.create_user(
            email='driver@test.com',
            password='testpass123',
            phone_number='+250788654321'
        )

        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            status=RideStatus.ONGOING
        )

    def test_update_driver_location(self):
        """Test updating driver location"""
        success = RealTimeTrackingService.update_driver_location(
            ride=self.ride,
            lat=-1.9500,
            lng=30.0610,
            speed_kmh=25.5
        )

        self.assertTrue(success)
        self.ride.refresh_from_db()
        self.assertEqual(float(self.ride.current_lat), -1.9500)
        self.assertEqual(float(self.ride.current_lng), 30.0610)

    def test_get_current_location(self):
        """Test getting current location"""
        # Update location first
        RealTimeTrackingService.update_driver_location(
            ride=self.ride,
            lat=-1.9500,
            lng=30.0610,
            speed_kmh=25.5
        )

        location = RealTimeTrackingService.get_current_location(self.ride.id)

        self.assertIsNotNone(location)
        self.assertEqual(location['lat'], -1.9500)
        self.assertEqual(location['lng'], 30.0610)

    def test_get_route_history(self):
        """Test getting route history"""
        # Create tracking points
        RideTracking.objects.create(
            ride=self.ride,
            lat=Decimal('-1.9536'),
            lng=Decimal('30.0606'),
            speed_kmh=20.0
        )
        RideTracking.objects.create(
            ride=self.ride,
            lat=Decimal('-1.9500'),
            lng=Decimal('30.0610'),
            speed_kmh=25.0
        )

        history = RealTimeTrackingService.get_route_history(self.ride.id)

        self.assertEqual(len(history), 2)
        self.assertIn('lat', history[0])
        self.assertIn('lng', history[0])


class PaymentIntegrationTests(TestCase):
    """Tests for payment processing"""

    def setUp(self):
        self.rider = User.objects.create_user(
            email='rider@test.com',
            password='testpass123',
            phone_number='+250788123456'
        )
        self.driver = User.objects.create_user(
            email='driver@test.com',
            password='testpass123',
            phone_number='+250788654321'
        )

        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9536'),
            pickup_lng=Decimal('30.0606'),
            dropoff_lat=Decimal('-1.9442'),
            dropoff_lng=Decimal('30.0619'),
            distance_km=Decimal('5.0'),
            final_fare=Decimal('4500.00'),
            status=RideStatus.COMPLETED
        )

    def test_process_payment_mtn_momo(self):
        """Test payment processing with MTN MoMo"""
        result = BookingService.process_payment(
            ride=self.ride,
            phone_number='+250788123456'  # MTN number
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.reference)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.payment_status, PaymentStatus.COMPLETED)

    def test_process_payment_airtel_money(self):
        """Test payment processing with Airtel Money"""
        result = BookingService.process_payment(
            ride=self.ride,
            phone_number='+250733456789'  # Airtel number
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.reference)


# Run with: python manage.py test rides.test_comprehensive
# Or with pytest: pytest rides/test_comprehensive.py -v
