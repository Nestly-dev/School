
import time
import psutil
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Health & Monitoring"],
    responses={200: dict},
    summary="Comprehensive system health check",
    description="""
    Returns detailed health status of all system components:
    - Database connectivity
    - Cache (Redis) connectivity
    - Disk space availability
    - Memory usage
    - API response time
    """
)
class DetailedHealthCheckView(APIView):
    """GET /api/health/detailed/"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        start_time = time.time()
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'components': {}
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status['components']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'message': f'Database error: {str(e)}'
            }
        
        # Check cache
        try:
            cache_key = 'health_check_test'
            cache.set(cache_key, 'test_value', 10)
            cached_value = cache.get(cache_key)
            if cached_value == 'test_value':
                health_status['components']['cache'] = {
                    'status': 'healthy',
                    'message': 'Cache connection successful'
                }
            else:
                raise Exception('Cache value mismatch')
        except Exception as e:
            health_status['status'] = 'degraded'
            health_status['components']['cache'] = {
                'status': 'unhealthy',
                'message': f'Cache error: {str(e)}'
            }
        
        # Check disk space
        try:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            health_status['components']['disk'] = {
                'status': 'healthy' if disk_percent < 85 else 'warning',
                'usage_percent': disk_percent,
                'free_gb': round(disk.free / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2)
            }
            if disk_percent >= 95:
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['components']['disk'] = {
                'status': 'unknown',
                'message': str(e)
            }
        
        # Check memory
        try:
            memory = psutil.virtual_memory()
            health_status['components']['memory'] = {
                'status': 'healthy' if memory.percent < 85 else 'warning',
                'usage_percent': memory.percent,
                'available_mb': round(memory.available / (1024**2), 2),
                'total_mb': round(memory.total / (1024**2), 2)
            }
        except Exception as e:
            health_status['components']['memory'] = {
                'status': 'unknown',
                'message': str(e)
            }
        
        # Response time
        response_time_ms = round((time.time() - start_time) * 1000, 2)
        health_status['response_time_ms'] = response_time_ms
        
        # Determine HTTP status code
        if health_status['status'] == 'healthy':
            status_code = status.HTTP_200_OK
        elif health_status['status'] == 'degraded':
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health_status, status=status_code)


@extend_schema(
    tags=["Health & Monitoring"],
    responses={200: dict},
    summary="System performance metrics",
    description="Real-time system performance metrics for monitoring dashboard"
)
class SystemMetricsView(APIView):
    """GET /api/monitoring/metrics/"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                net_io = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                }
            except:
                network_stats = None
            
            # Database metrics
            from django.db import connection
            db_queries = len(connection.queries) if settings.DEBUG else None
            
            # Cache metrics (from common.cache)
            from common.cache import CACHE_METRICS
            cache_snapshot = CACHE_METRICS.snapshot()
            
            return Response({
                'timestamp': timezone.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                },
                'memory': {
                    'total_mb': round(memory.total / (1024**2), 2),
                    'available_mb': round(memory.available / (1024**2), 2),
                    'used_mb': round(memory.used / (1024**2), 2),
                    'percent': memory.percent,
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'percent': disk.percent,
                },
                'network': network_stats,
                'cache': cache_snapshot,
                'database': {
                    'queries_count': db_queries,
                }
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to collect metrics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["Health & Monitoring"],
    responses={200: dict},
    summary="Application logs (admin only)",
    description="Recent application logs for debugging"
)
class ApplicationLogsView(APIView):
    """GET /api/monitoring/logs/"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        try:
            log_file = settings.BASE_DIR / 'logs' / 'safeboda.log'
            lines = int(request.query_params.get('lines', 100))
            level = request.query_params.get('level', '').upper()
            
            if not log_file.exists():
                return Response({
                    'message': 'Log file not found',
                    'logs': []
                })
            
            # Read last N lines
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]
            
            # Filter by log level if specified
            if level:
                recent_lines = [
                    line for line in recent_lines
                    if level in line
                ]
            
            return Response({
                'log_file': str(log_file),
                'lines_requested': lines,
                'lines_returned': len(recent_lines),
                'filter_level': level or 'ALL',
                'logs': recent_lines
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to read logs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["Admin"],
    request={'type': 'object'},
    responses={200: dict},
    summary="Trigger manual database backup",
    description="Manually trigger database backup (admin only)"
)
class TriggerBackupView(APIView):
    """POST /api/admin/backup/trigger/"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        try:
            from django.core.management import call_command
            import os
            from datetime import datetime
            
            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = settings.BACKUP_DIR / f'backup_{timestamp}.json'
            
            # Run dumpdata command
            with open(backup_file, 'w') as f:
                call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)
            
            # Get file size
            file_size_mb = round(os.path.getsize(backup_file) / (1024**2), 2)
            
            return Response({
                'status': 'success',
                'message': 'Backup created successfully',
                'backup_file': str(backup_file),
                'size_mb': file_size_mb,
                'timestamp': timestamp
            })
        except Exception as e:
            return Response(
                {'error': f'Backup failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["Admin"],
    responses={200: dict},
    summary="System status dashboard",
    description="Comprehensive system status for admin dashboard"
)
class SystemStatusView(APIView):
    """GET /api/admin/system/status/"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        from rides.models import Ride, RideStatus
        from locations.models import DriverLocation
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # System uptime (approximate based on server start)
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
        except:
            uptime_days = uptime_hours = None
        
        # Active rides
        active_rides = Ride.objects.filter(
            status__in=[
                RideStatus.SEARCHING,
                RideStatus.ACCEPTED,
                RideStatus.DRIVER_ARRIVING,
                RideStatus.ARRIVED,
                RideStatus.ONGOING
            ]
        ).count()
        
        # Online drivers
        online_drivers = DriverLocation.objects.filter(is_online=True).count()
        
        # Total users
        total_users = User.objects.filter(is_active=True).count()
        
        # Today's stats
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_rides = Ride.objects.filter(created_at__gte=today_start).count()
        today_completed = Ride.objects.filter(
            created_at__gte=today_start,
            status=RideStatus.COMPLETED
        ).count()
        
        return Response({
            'timestamp': timezone.now().isoformat(),
            'system': {
                'uptime_days': uptime_days,
                'uptime_hours': uptime_hours,
                'debug_mode': settings.DEBUG,
                'environment': 'production' if not settings.DEBUG else 'development',
            },
            'application': {
                'active_rides': active_rides,
                'online_drivers': online_drivers,
                'total_users': total_users,
                'today_rides': today_rides,
                'today_completed': today_completed,
            },
            'version': {
                'api_version': '1.0.0',
                'django_version': '5.2.7',
            }
        })


@extend_schema(
    tags=["Admin"],
    request={'type': 'object', 'properties': {
        'enabled': {'type': 'boolean'}
    }},
    responses={200: dict},
    summary="Enable/disable maintenance mode",
    description="Put system in maintenance mode (blocks non-admin requests)"
)
class MaintenanceModeView(APIView):
    """POST /api/admin/maintenance/enable/"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        enabled = request.data.get('enabled', True)
        
        # Store maintenance mode flag in cache
        cache.set('maintenance_mode', enabled, timeout=None)
        
        return Response({
            'maintenance_mode': enabled,
            'message': 'Maintenance mode enabled' if enabled else 'Maintenance mode disabled',
            'timestamp': timezone.now().isoformat()
        })
    
    def get(self, request):
        """Check current maintenance mode status"""
        maintenance_mode = cache.get('maintenance_mode', False)
        
        return Response({
            'maintenance_mode': maintenance_mode,
            'timestamp': timezone.now().isoformat()
        })