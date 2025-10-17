"""
Complete booking workflow API endpoints
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Ride, Notification, RideStatus
from .services import BookingService, RealTimeTrackingService
from .serializers import (
    CreateBookingSerializer,
    BookingDetailSerializer,
    UpdateBookingStatusSerializer,
    CancelBookingSerializer,
    ActiveBookingsSerializer,
    ProcessPaymentSerializer,
    RealTimeLocationSerializer,
    NotificationSerializer
)
from common.pagination import SmallPageNumberPagination


@extend_schema(
    tags=["Bookings"],
    request=CreateBookingSerializer,
    responses={201: BookingDetailSerializer, 400: dict},
    summary="Create new ride booking",
    description="""
    Create a new ride booking with integrated services:
    - Finds nearby available drivers
    - Calculates route and fare estimate
    - Geocodes pickup and dropoff addresses
    - Sends notifications to drivers
    
    Returns booking details with list of nearby drivers.
    """
)
class CreateBookingView(APIView):
    """POST /api/bookings/create/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use integrated booking service
        result = BookingService.create_booking(
            rider=request.user,
            pickup_lat=serializer.validated_data['pickup_lat'],
            pickup_lng=serializer.validated_data['pickup_lng'],
            dropoff_lat=serializer.validated_data['dropoff_lat'],
            dropoff_lng=serializer.validated_data['dropoff_lng'],
            payment_method=serializer.validated_data.get('payment_method', 'MTN_MOMO')
        )
        
        if not result.success:
            return Response(
                {'error': result.error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'booking': BookingDetailSerializer(result.ride).data,
                'nearby_drivers': result.nearby_drivers,
                'message': 'Booking created successfully. Searching for drivers...'
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Bookings"],
    responses={200: BookingDetailSerializer, 404: dict},
    summary="Get booking details"
)
class BookingDetailView(APIView):
    """GET /api/bookings/{id}/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        ride = get_object_or_404(
            Ride.objects.select_related('rider', 'driver'),
            pk=pk
        )
        
        # Ensure user is part of this ride
        if request.user not in [ride.rider, ride.driver]:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(BookingDetailSerializer(ride).data)


@extend_schema(
    tags=["Bookings"],
    request=UpdateBookingStatusSerializer,
    responses={200: BookingDetailSerializer, 400: dict},
    summary="Update booking status",
    description="""
    Update ride status through workflow:
    - SEARCHING -> ACCEPTED (driver accepts)
    - ACCEPTED -> DRIVER_ARRIVING (driver near pickup)
    - DRIVER_ARRIVING -> ARRIVED (driver at pickup)
    - ARRIVED -> ONGOING (ride starts)
    - ONGOING -> COMPLETED (ride ends)
    """
)
class UpdateBookingStatusView(APIView):
    """PUT /api/bookings/{id}/status/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk)
        serializer = UpdateBookingStatusSerializer(
            data=request.data,
            context={'ride': ride, 'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        action = serializer.validated_data.get('action')
        
        success = False
        
        # Handle different status transitions
        if action == 'accept' and ride.status == RideStatus.SEARCHING:
            success = BookingService.accept_ride(ride, request.user)
            
        elif action == 'arrive' and ride.status == RideStatus.DRIVER_ARRIVING:
            ride.update_status(RideStatus.ARRIVED, user=request.user)
            success = True
            
        elif action == 'start' and ride.status == RideStatus.ARRIVED:
            success = BookingService.start_ride(ride, request.user)
            
        elif action == 'complete' and ride.status == RideStatus.ONGOING:
            success = BookingService.complete_ride(ride, request.user)
        
        if not success:
            return Response(
                {'error': 'Invalid status transition'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ride.refresh_from_db()
        return Response(BookingDetailSerializer(ride).data)


@extend_schema(
    tags=["Bookings"],
    request=CancelBookingSerializer,
    responses={200: dict},
    summary="Cancel booking"
)
class CancelBookingView(APIView):
    """POST /api/bookings/{id}/cancel/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk)
        serializer = CancelBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        success = BookingService.cancel_ride(
            ride,
            request.user,
            reason=serializer.validated_data.get('reason', '')
        )
        
        if not success:
            return Response(
                {'error': 'Cannot cancel this booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': 'Booking cancelled successfully'})


@extend_schema(
    tags=["Bookings"],
    responses={200: ActiveBookingsSerializer(many=True)},
    summary="Get active bookings",
    description="Returns all active bookings for the authenticated user (as rider or driver)"
)
class ActiveBookingsView(generics.ListAPIView):
    """GET /api/bookings/active/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActiveBookingsSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Ride.objects.filter(
            Q(rider=user) | Q(driver=user),
            status__in=[
                RideStatus.SEARCHING,
                RideStatus.ACCEPTED,
                RideStatus.DRIVER_ARRIVING,
                RideStatus.ARRIVED,
                RideStatus.ONGOING
            ]
        ).select_related('rider', 'driver').order_by('-created_at')


@extend_schema(
    tags=["Payments"],
    request=ProcessPaymentSerializer,
    responses={200: dict, 400: dict},
    summary="Process payment for completed ride",
    description="""
    Process payment via Rwanda mobile money (MTN MoMo or Airtel Money).
    Phone number format determines provider:
    - +25078xxxxxxx or 078xxxxxxx -> MTN MoMo
    - +25073xxxxxxx or 073xxxxxxx -> Airtel Money
    """
)
class ProcessPaymentView(APIView):
    """POST /api/payments/process/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ProcessPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ride = get_object_or_404(Ride, pk=serializer.validated_data['booking_id'])
        
        # Verify user is the rider
        if ride.rider != request.user:
            return Response(
                {'error': 'Only the rider can process payment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify ride is completed
        if ride.status != RideStatus.COMPLETED:
            return Response(
                {'error': 'Ride must be completed before payment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process payment
        result = BookingService.process_payment(
            ride,
            phone_number=serializer.validated_data['phone_number']
        )
        
        if not result.success:
            return Response(
                {'error': result.error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'success': True,
            'reference': result.reference,
            'amount': float(ride.final_fare or ride.fare_estimate),
            'message': 'Payment processed successfully'
        })


@extend_schema(
    tags=["Real-Time Tracking"],
    responses={200: RealTimeLocationSerializer, 404: dict},
    summary="Get real-time location updates",
    description="Get current driver location during active ride (polling endpoint)"
)
class RealTimeTrackingView(APIView):
    """GET /api/realtime/tracking/{booking_id}/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, booking_id):
        ride = get_object_or_404(Ride, pk=booking_id)
        
        # Verify user is part of this ride
        if request.user not in [ride.rider, ride.driver]:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get current location
        location = RealTimeTrackingService.get_current_location(booking_id)
        
        if not location:
            return Response(
                {'error': 'No location data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'booking_id': booking_id,
            'status': ride.status,
            'driver_location': location,
            'pickup_location': {
                'lat': float(ride.pickup_lat),
                'lng': float(ride.pickup_lng)
            },
            'dropoff_location': {
                'lat': float(ride.dropoff_lat),
                'lng': float(ride.dropoff_lng)
            }
        })


@extend_schema(
    tags=["Real-Time Tracking"],
    request=RealTimeLocationSerializer,
    responses={200: dict},
    summary="Update driver location during ride",
    description="Driver updates their location during active ride (called frequently)"
)
class UpdateDriverLocationView(APIView):
    """POST /api/realtime/location/update/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = RealTimeLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ride = get_object_or_404(Ride, pk=serializer.validated_data['booking_id'])
        
        # Verify user is the driver
        if ride.driver != request.user:
            return Response(
                {'error': 'Only the driver can update location'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        success = RealTimeTrackingService.update_driver_location(
            ride,
            lat=serializer.validated_data['lat'],
            lng=serializer.validated_data['lng'],
            speed_kmh=serializer.validated_data.get('speed_kmh', 0),
            heading=serializer.validated_data.get('heading')
        )
        
        if not success:
            return Response(
                {'error': 'Cannot update location for this ride'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': 'Location updated successfully'})


@extend_schema(
    tags=["Notifications"],
    responses={200: NotificationSerializer(many=True)},
    summary="Get user notifications",
    parameters=[
        OpenApiParameter(
            name='unread_only',
            type=bool,
            location=OpenApiParameter.QUERY,
            description='Filter to unread notifications only'
        )
    ]
)
class NotificationsView(generics.ListAPIView):
    """GET /api/notifications/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = SmallPageNumberPagination
    
    def get_queryset(self):
        queryset = Notification.objects.filter(
            user=self.request.user
        ).select_related('ride').order_by('-created_at')
        
        if self.request.query_params.get('unread_only') == 'true':
            queryset = queryset.filter(is_read=False)
        
        return queryset


@extend_schema(
    tags=["Notifications"],
    responses={200: dict},
    summary="Mark notification as read"
)
class MarkNotificationReadView(APIView):
    """POST /api/notifications/{id}/read/"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'Notification marked as read'})


@extend_schema(
    tags=["Notifications"],
    request={'type': 'object', 'properties': {
        'user_ids': {'type': 'array', 'items': {'type': 'integer'}},
        'title': {'type': 'string'},
        'message': {'type': 'string'},
        'notification_type': {'type': 'string'}
    }},
    responses={200: dict},
    summary="Send notifications (admin only)",
    description="Send custom notifications to specific users"
)
class SendNotificationView(APIView):
    """POST /api/notifications/send/"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        user_ids = request.data.get('user_ids', [])
        title = request.data.get('title', '')
        message = request.data.get('message', '')
        notification_type = request.data.get(
            'notification_type',
            'RIDE_REQUEST'
        )
        
        if not user_ids or not title or not message:
            return Response(
                {'error': 'user_ids, title, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create notifications
        notifications = [
            Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message
            )
            for user_id in user_ids
        ]
        
        Notification.objects.bulk_create(notifications)
        
        return Response({
            'message': f'Notifications sent to {len(user_ids)} users'
        })


# =============================================================================
# Legacy Views (backward compatibility)
# =============================================================================

@extend_schema(
    tags=["Rides - Legacy"],
    request=CreateBookingSerializer,
    responses={201: BookingDetailSerializer, 400: dict},
    summary="Request a ride (legacy endpoint)",
    description="Legacy endpoint for ride requests. Use /api/bookings/create/ instead."
)
class RequestRideView(CreateBookingView):
    """POST /api/rides/request/ - Legacy alias for CreateBookingView"""
    pass


@extend_schema(
    tags=["Rides - Legacy"],
    responses={200: BookingDetailSerializer, 404: dict},
    summary="Get ride details (legacy endpoint)",
    description="Legacy endpoint for ride details. Use /api/bookings/{id}/ instead."
)
class RideDetailView(BookingDetailView):
    """GET /api/rides/{id}/ - Legacy alias for BookingDetailView"""
    pass


@extend_schema(
    tags=["Rides - Legacy"],
    responses={200: ActiveBookingsSerializer(many=True)},
    summary="Get ride history (legacy endpoint)",
    description="Returns completed and cancelled rides for the authenticated user"
)
class RideHistoryView(generics.ListAPIView):
    """GET /api/rides/history/ - Historical rides only"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActiveBookingsSerializer
    pagination_class = SmallPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Ride.objects.filter(
            Q(rider=user) | Q(driver=user),
            status__in=[RideStatus.COMPLETED, RideStatus.CANCELLED]
        ).select_related('rider', 'driver').order_by('-created_at')


@extend_schema(
    tags=["Rides - Legacy"],
    responses={200: ActiveBookingsSerializer(many=True)},
    summary="Get my rides (legacy endpoint)",
    description="Returns all rides for the authenticated user (active + history)"
)
class MyRidesView(generics.ListAPIView):
    """GET /api/rides/mine/ - All rides for current user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActiveBookingsSerializer
    pagination_class = SmallPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return Ride.objects.filter(
            Q(rider=user) | Q(driver=user)
        ).select_related('rider', 'driver').order_by('-created_at')