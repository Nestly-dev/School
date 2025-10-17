from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class RideStatus(models.TextChoices):
    """Enhanced ride status flow"""
    REQUESTED = "REQUESTED", "Requested"
    SEARCHING = "SEARCHING", "Searching for Driver"
    ACCEPTED = "ACCEPTED", "Accepted"
    DRIVER_ARRIVING = "DRIVER_ARRIVING", "Driver Arriving"
    ARRIVED = "ARRIVED", "Driver Arrived"
    ONGOING = "ONGOING", "Ongoing"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    FAILED = "FAILED", "Failed"


class PaymentStatus(models.TextChoices):
    """Payment workflow status"""
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"


class PaymentMethod(models.TextChoices):
    """Rwanda mobile money providers"""
    MTN_MOMO = "MTN_MOMO", "MTN Mobile Money"
    AIRTEL_MONEY = "AIRTEL_MONEY", "Airtel Money"
    CASH = "CASH", "Cash"
    CARD = "CARD", "Card"


class Ride(models.Model):
    """Enhanced ride model with real-time tracking support"""
    
    # Basic Information
    rider = models.ForeignKey(
        User, 
        related_name="rides_as_rider", 
        on_delete=models.CASCADE
    )
    driver = models.ForeignKey(
        User, 
        related_name="rides_as_driver", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Location Details
    pickup_address = models.CharField(max_length=255, blank=True)
    dropoff_address = models.CharField(max_length=255, blank=True)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lat = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Current Location (for real-time tracking)
    current_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Current driver location during ride"
    )
    current_lng = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Current driver location during ride"
    )
    
    # Distance & Pricing
    distance_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    fare_estimate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Estimated fare in RWF"
    )
    final_fare = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Actual fare charged in RWF"
    )
    
    # Status & Workflow
    status = models.CharField(
        max_length=20, 
        choices=RideStatus.choices, 
        default=RideStatus.REQUESTED,
        db_index=True
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MTN_MOMO
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Mobile money transaction reference"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    cancel_reason = models.CharField(max_length=255, blank=True)
    cancelled_by = models.ForeignKey(
        User,
        related_name="cancelled_rides",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Rating & Feedback
    rider_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Rider's rating of driver (1-5)"
    )
    driver_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Driver's rating of rider (1-5)"
    )
    rider_feedback = models.TextField(blank=True)
    driver_feedback = models.TextField(blank=True)
    
    # Government Reporting
    reported_to_rtda = models.BooleanField(
        default=False,
        help_text="Whether ride has been reported to RTDA"
    )
    rtda_report_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["rider", "-created_at"]),
            models.Index(fields=["driver", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return (
            f"Ride #{self.pk} {self.status} "
            f"(rider={self.rider_id}, driver={self.driver_id})"
        )
    
    @staticmethod
    def price_for(
        distance_km: Decimal, 
        base: Decimal = Decimal("500"), 
        per_km: Decimal = Decimal("800")
    ) -> Decimal:
        """
        Calculate fare based on Rwanda pricing model
        Base: 500 RWF + 800 RWF per km
        """
        amount = base + (per_km * (distance_km or Decimal("0")))
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def update_status(self, new_status: str, user=None):
        """Update ride status with timestamp tracking"""
        self.status = new_status
        now = timezone.now()
        
        if new_status == RideStatus.ACCEPTED:
            self.accepted_at = now
        elif new_status == RideStatus.ONGOING:
            self.started_at = now
        elif new_status == RideStatus.COMPLETED:
            self.completed_at = now
            # Calculate final fare if not set
            if not self.final_fare and self.distance_km:
                self.final_fare = self.price_for(self.distance_km)
        elif new_status == RideStatus.CANCELLED:
            self.cancelled_at = now
            self.cancelled_by = user
        
        self.save()
    
    def calculate_duration_minutes(self) -> int:
        """Calculate ride duration in minutes"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return 0
    
    def is_active(self) -> bool:
        """Check if ride is currently active"""
        return self.status in [
            RideStatus.REQUESTED,
            RideStatus.SEARCHING,
            RideStatus.ACCEPTED,
            RideStatus.DRIVER_ARRIVING,
            RideStatus.ARRIVED,
            RideStatus.ONGOING
        ]


class RideTracking(models.Model):
    """Real-time location tracking during rides"""
    ride = models.ForeignKey(
        Ride,
        related_name="tracking_points",
        on_delete=models.CASCADE
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.FloatField(default=0)
    heading = models.FloatField(null=True, blank=True)
    accuracy_m = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["ride", "-timestamp"]),
        ]
    
    def __str__(self):
        return f"Tracking point for Ride #{self.ride_id} at {self.timestamp}"


class Notification(models.Model):
    """Notification system for riders and drivers"""
    
    class NotificationType(models.TextChoices):
        RIDE_REQUEST = "RIDE_REQUEST", "Ride Request"
        RIDE_ACCEPTED = "RIDE_ACCEPTED", "Ride Accepted"
        DRIVER_ARRIVING = "DRIVER_ARRIVING", "Driver Arriving"
        RIDE_STARTED = "RIDE_STARTED", "Ride Started"
        RIDE_COMPLETED = "RIDE_COMPLETED", "Ride Completed"
        RIDE_CANCELLED = "RIDE_CANCELLED", "Ride Cancelled"
        PAYMENT_SUCCESS = "PAYMENT_SUCCESS", "Payment Successful"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"
        DRIVER_NEARBY = "DRIVER_NEARBY", "Driver Nearby"
    
    user = models.ForeignKey(
        User,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    ride = models.ForeignKey(
        Ride,
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.user}"