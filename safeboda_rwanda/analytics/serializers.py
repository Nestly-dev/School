"""
Serializers for Analytics API
"""
from rest_framework import serializers
from datetime import date


class RidePatternsSerializer(serializers.Serializer):
    """Ride patterns analytics output"""
    period = serializers.CharField()
    total_rides = serializers.IntegerField()
    avg_rides_per_day = serializers.FloatField()
    peak_hours = serializers.ListField()
    day_of_week_distribution = serializers.DictField()
    hourly_distribution = serializers.DictField()
    trend_data = serializers.ListField()


class DriverPerformanceSerializer(serializers.Serializer):
    """Driver performance metrics output"""
    driver_id = serializers.IntegerField()
    total_rides = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_rating = serializers.FloatField()
    acceptance_rate = serializers.FloatField()
    cancellation_rate = serializers.FloatField()
    earnings_per_hour = serializers.DecimalField(max_digits=10, decimal_places=2)


class RevenueSummarySerializer(serializers.Serializer):
    """Revenue analytics output"""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    platform_commission = serializers.DecimalField(max_digits=15, decimal_places=2)
    driver_earnings = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_fare = serializers.DecimalField(max_digits=10, decimal_places=2)
    growth_rate = serializers.FloatField()
    revenue_by_payment_method = serializers.DictField()
    daily_revenue_trend = serializers.ListField()


class TrafficHotspotsSerializer(serializers.Serializer):
    """Traffic hotspots analytics output"""
    hotspots = serializers.ListField()
    popular_routes = serializers.ListField()
    peak_hour_locations = serializers.DictField()
    underserved_areas = serializers.ListField()


class UserBehaviorSerializer(serializers.Serializer):
    """User behavior analytics output"""
    total_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    returning_users = serializers.IntegerField()
    retention_rate = serializers.DictField()
    avg_rides_per_user = serializers.FloatField()
    churn_rate = serializers.FloatField()
    cohort_analysis = serializers.DictField()


class CustomReportSerializer(serializers.Serializer):
    """Custom report generation request"""
    report_type = serializers.ChoiceField(
        choices=[
            'executive_summary',
            'operational',
            'financial',
            'growth',
            'regulatory'
        ],
        required=True
    )
    period_start = serializers.DateField(required=True)
    period_end = serializers.DateField(required=True)
    metrics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    filters = serializers.DictField(required=False, default=dict)
    format = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf'],
        default='json'
    )

    def validate(self, data):
        """Validate date range"""
        if data['period_start'] > data['period_end']:
            raise serializers.ValidationError(
                "period_start must be before period_end"
            )
        return data
