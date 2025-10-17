"""
Serializers for booking workflow
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ride, RideStatus, Notification, PaymentMethod

User = get_user_model()


class CreateBookingSerializer(serializers.Serializer):
    """Create new booking request"""
    pickup_lat = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6,
        min_value=-90,
        max_value=90
    )
    pickup_lng = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180
    )
    dropoff_lat = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90
    )
    dropoff_lng = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180
    )
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.MTN_MOMO
    )


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for bookings"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = fields


class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed booking information"""
    rider = UserBasicSerializer(read_only=True)
    driver = UserBasicSerializer(read_only=True, allow_null=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    payment_status_display = serializers.CharField(
        source='get_payment_status_display',
        read_only=True
    )
    duration_minutes = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = [
            'id',
            'rider',
            'driver',
            'status',
            'status_display',
            'pickup_address',
            'dropoff_address',
            'pickup_lat',
            'pickup_lng',
            'dropoff_lat',
            'dropoff_lng',
            'current_lat',
            'current_lng',
            'distance_km',
            'fare_estimate',
            'final_fare',
            'payment_method',
            'payment_method_display',
            'payment_status',
            'payment_status_display',
            'payment_reference',
            'created_at',
            'accepted_at',
            'started_at',
            'completed_at',
            'cancelled_at',
            'cancel_reason',
            'duration_minutes',
            'is_active',
            'rider_rating',
            'driver_rating',
        ]
        read_only_fields = fields
    
    def get_duration_minutes(self, obj):
        return obj.calculate_duration_minutes()
    
    def get_is_active(self, obj):
        return obj.is_active()


class ActiveBookingsSerializer(serializers.ModelSerializer):
    """Lightweight serializer for active bookings list"""
    rider_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = Ride
        fields = [
            'id',
            'status',
            'status_display',
            'rider_name',
            'driver_name',
            'pickup_address',
            'dropoff_address',
            'distance_km',
            'fare_estimate',
            'created_at',
            'current_lat',
            'current_lng'
        ]
        read_only_fields = fields
    
    def get_rider_name(self, obj):
        return f"{obj.rider.first_name} {obj.rider.last_name}".strip() or obj.rider.username
    
    def get_driver_name(self, obj):
        if obj.driver:
            return f"{obj.driver.first_name} {obj.driver.last_name}".strip() or obj.driver.username
        return None


class UpdateBookingStatusSerializer(serializers.Serializer):
    """Update booking status"""
    status = serializers.ChoiceField(
        choices=RideStatus.choices,
        required=False
    )
    action = serializers.ChoiceField(
        choices=['accept', 'arrive', 'start', 'complete'],
        required=False
    )
    
    def validate(self, data):
        ride = self.context.get('ride')
        user = self.context.get('user')
        action = data.get('action')
        
        # Validate permissions based on action
        if action == 'accept':
            # Only drivers can accept
            if not hasattr(user, 'driver_location'):
                raise serializers.ValidationError(
                    "Only drivers can accept rides"
                )
        elif action in ['arrive', 'start', 'complete']:
            # Only assigned driver can perform these actions
            if ride.driver != user:
                raise serializers.ValidationError(
                    "Only the assigned driver can perform this action"
                )
        
        return data


class CancelBookingSerializer(serializers.Serializer):
    """Cancel booking with reason"""
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )


class ProcessPaymentSerializer(serializers.Serializer):
    """Process payment for completed ride"""
    booking_id = serializers.IntegerField()
    phone_number = serializers.CharField(
        max_length=15,
        help_text="Rwanda phone number (+25078xxxxxxx or 078xxxxxxx)"
    )
    
    def validate_phone_number(self, value):
        """Validate Rwanda phone number format"""
        # Remove spaces and dashes
        phone = value.replace(' ', '').replace('-', '')
        
        # Accept formats: +25078xxxxxxx, +25073xxxxxxx, 078xxxxxxx, 073xxxxxxx
        valid_prefixes = ['+25078', '+25073', '078', '073']
        
        if not any(phone.startswith(prefix) for prefix in valid_prefixes):
            raise serializers.ValidationError(
                "Invalid Rwanda phone number. Must start with +25078/+25073 (MTN) or 078/073 (MTN/Airtel)"
            )
        
        return phone


class RealTimeLocationSerializer(serializers.Serializer):
    """Real-time location update"""
    booking_id = serializers.IntegerField()
    lat = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90
    )
    lng = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180
    )
    speed_kmh = serializers.FloatField(
        required=False,
        default=0,
        min_value=0
    )
    heading = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=359
    )


class NotificationSerializer(serializers.ModelSerializer):
    """Notification details"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    ride_id = serializers.IntegerField(
        source='ride.id',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'notification_type_display',
            'title',
            'message',
            'is_read',
            'created_at',
            'ride_id'
        ]
        read_only_fields = fields


class RideRatingSerializer(serializers.Serializer):
    """Rate completed ride"""
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )