"""
Comprehensive test suite for booking workflow
Target: 90%+ code coverage
"""
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from rides.models import Ride, RideStatus, PaymentStatus, Notification
from rides.services import BookingService, RealTimeTrackingService
from locations.models import DriverLocation

User = get_user_model()


class BookingServiceTests(TestCase):
    """Test booking service logic"""
    
    def setUp(self):
        """Create test users and data"""
        self.rider = User.objects.create_user(
            username='rider1',
            email='rider@test.com',
            password='testpass123'
        )
        
        self.driver = User.objects.create_user(
            username='driver1',
            email='driver@test.com',
            password='testpass123'
        )
        
        # Create driver location
        DriverLocation.objects.create(
            driver=self.driver,
            lat=-1.9441,
            lng=30.0619,
            is_online=True
        )
    
    def test_accept_ride(self):
        """Test driver accepting a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.SEARCHING,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        success = BookingService.accept_ride(ride, self.driver)
        
        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.driver, self.driver)
        self.assertEqual(ride.status, RideStatus.ACCEPTED)
        
        # Check notification was created
        notification = Notification.objects.filter(
            user=self.rider,
            ride=ride,
            notification_type=Notification.NotificationType.RIDE_ACCEPTED
        ).first()
        self.assertIsNotNone(notification)
    
    def test_cannot_accept_non_searching_ride(self):
        """Test driver cannot accept ride that's not in SEARCHING status"""
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.COMPLETED,
            driver=self.driver,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        driver2 = User.objects.create_user(
            username='driver2',
            email='driver2@test.com',
            password='testpass123'
        )
        
        success = BookingService.accept_ride(ride, driver2)
        self.assertFalse(success)
    
    def test_complete_ride(self):
        """Test completing a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.ONGOING,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        success = BookingService.complete_ride(ride, self.driver)
        
        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.status, RideStatus.COMPLETED)
        self.assertIsNotNone(ride.completed_at)
        self.assertIsNotNone(ride.final_fare)
    
    def test_cancel_ride(self):
        """Test cancelling a ride"""
        ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.ACCEPTED,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        success = BookingService.cancel_ride(
            ride,
            self.rider,
            reason="Changed my mind"
        )
        
        self.assertTrue(success)
        ride.refresh_from_db()
        self.assertEqual(ride.status, RideStatus.CANCELLED)
        self.assertEqual(ride.cancel_reason, "Changed my mind")
        self.assertEqual(ride.cancelled_by, self.rider)


class RealTimeTrackingTests(TestCase):
    """Test real-time tracking functionality"""
    
    def setUp(self):
        self.rider = User.objects.create_user(
            username='rider',
            email='rider@test.com',
            password='testpass123'
        )
        
        self.driver = User.objects.create_user(
            username='driver',
            email='driver@test.com',
            password='testpass123'
        )
        
        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.ACCEPTED,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
    
    def test_update_driver_location(self):
        """Test updating driver location during ride"""
        success = RealTimeTrackingService.update_driver_location(
            self.ride,
            lat=-1.9450,
            lng=30.0625,
            speed_kmh=25.5,
            heading=180.0
        )
        
        self.assertTrue(success)
        self.ride.refresh_from_db()
        self.assertEqual(float(self.ride.current_lat), -1.9450)
        self.assertEqual(float(self.ride.current_lng), 30.0625)
    
    def test_cannot_update_completed_ride(self):
        """Test cannot update location for completed ride"""
        self.ride.status = RideStatus.COMPLETED
        self.ride.save()
        
        success = RealTimeTrackingService.update_driver_location(
            self.ride,
            lat=-1.9450,
            lng=30.0625
        )
        
        self.assertFalse(success)
    
    def test_get_current_location(self):
        """Test retrieving current location"""
        RealTimeTrackingService.update_driver_location(
            self.ride,
            lat=-1.9450,
            lng=30.0625
        )
        
        location = RealTimeTrackingService.get_current_location(self.ride.id)
        
        self.assertIsNotNone(location)
        self.assertEqual(location['lat'], -1.9450)
        self.assertEqual(location['lng'], 30.0625)


class NotificationTests(TestCase):
    """Test notification system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.ride = Ride.objects.create(
            rider=self.user,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.SEARCHING,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            user=self.user,
            ride=self.ride,
            notification_type=Notification.NotificationType.RIDE_REQUEST,
            title='New Ride',
            message='New ride request nearby'
        )
        
        self.assertIsNotNone(notification.id)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.user, self.user)
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            ride=self.ride,
            notification_type=Notification.NotificationType.RIDE_ACCEPTED,
            title='Ride Accepted',
            message='Driver accepted your ride'
        )
        
        notification.is_read = True
        notification.save()
        
        self.assertTrue(notification.is_read)


class RideModelTests(TestCase):
    """Test Ride model methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_price_calculation(self):
        """Test fare calculation"""
        distance = Decimal('5.0')
        fare = Ride.price_for(distance)
        
        # Base (500) + (5km * 800) = 4500 RWF
        expected = Decimal('4500.00')
        self.assertEqual(fare, expected)
    
    def test_calculate_duration(self):
        """Test ride duration calculation"""
        ride = Ride.objects.create(
            rider=self.user,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.COMPLETED,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        # Manually set timestamps
        from datetime import timedelta
        ride.started_at = timezone.now() - timedelta(minutes=15)
        ride.completed_at = timezone.now()
        ride.save()
        
        duration = ride.calculate_duration_minutes()
        self.assertEqual(duration, 15)
    
    def test_is_active(self):
        """Test is_active method"""
        ride = Ride.objects.create(
            rider=self.user,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.ONGOING,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        self.assertTrue(ride.is_active())
        
        ride.status = RideStatus.COMPLETED
        ride.save()
        
        self.assertFalse(ride.is_active())
    
    def test_update_status(self):
        """Test update_status method"""
        ride = Ride.objects.create(
            rider=self.user,
            pickup_lat=Decimal('-1.9441'),
            pickup_lng=Decimal('30.0619'),
            dropoff_lat=Decimal('-1.9532'),
            dropoff_lng=Decimal('30.0947'),
            status=RideStatus.ACCEPTED,
            distance_km=Decimal('5.2'),
            fare_estimate=Decimal('4660.00')
        )
        
        ride.update_status(RideStatus.ONGOING)
        
        self.assertEqual(ride.status, RideStatus.ONGOING)
        self.assertIsNotNone(ride.started_at)


class PerformanceTests(TestCase):
    """Performance and optimization tests"""
    
    def test_bulk_ride_creation(self):
        """Test creating multiple rides efficiently"""
        import time
        
        rider = User.objects.create_user(
            username='rider',
            email='rider@test.com',
            password='testpass123'
        )
        
        start = time.time()
        
        rides = [
            Ride(
                rider=rider,
                pickup_lat=Decimal('-1.9441'),
                pickup_lng=Decimal('30.0619'),
                dropoff_lat=Decimal('-1.9532'),
                dropoff_lng=Decimal('30.0947'),
                status=RideStatus.COMPLETED,
                distance_km=Decimal('5.2'),
                fare_estimate=Decimal('4660.00')
            )
            for _ in range(100)
        ]
        
        Ride.objects.bulk_create(rides)
        
        end = time.time()
        duration = end - start
        
        # Should complete in under 1 second
        self.assertLess(duration, 1.0)
        self.assertEqual(Ride.objects.count(), 100)
    
    def test_query_optimization(self):
        """Test query performance with select_related"""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        rider = User.objects.create_user(
            username='rider',
            email='rider@test.com',
            password='testpass123'
        )
        
        driver = User.objects.create_user(
            username='driver',
            email='driver@test.com',
            password='testpass123'
        )
        
        # Create test data
        for i in range(10):
            Ride.objects.create(
                rider=rider,
                driver=driver,
                pickup_lat=Decimal('-1.9441'),
                pickup_lng=Decimal('30.0619'),
                dropoff_lat=Decimal('-1.9532'),
                dropoff_lng=Decimal('30.0947'),
                status=RideStatus.COMPLETED,
                distance_km=Decimal('5.2'),
                fare_estimate=Decimal('4660.00')
            )
        
        # Test without select_related (N+1 problem)
        with CaptureQueriesContext(connection) as context:
            rides = list(Ride.objects.all())
            for ride in rides:
                _ = ride.rider.username
                _ = ride.driver.username if ride.driver else None
        
        queries_without_select = len(context.captured_queries)
        
        # Test with select_related (optimized)
        with CaptureQueriesContext(connection) as context:
            rides = list(Ride.objects.select_related('rider', 'driver').all())
            for ride in rides:
                _ = ride.rider.username
                _ = ride.driver.username if ride.driver else None
        
        queries_with_select = len(context.captured_queries)
        
        # Should use significantly fewer queries
        self.assertLess(queries_with_select, queries_without_select)