from rest_framework import serializers


class PointSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    lng = serializers.FloatField(min_value=-180.0, max_value=180.0)


class NearbyDriversRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    lng = serializers.FloatField(min_value=-180.0, max_value=180.0)
    radius_km = serializers.FloatField(min_value=0.1, max_value=20.0, default=3.0)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=20)


class DriverSummarySerializer(serializers.Serializer):
    driver_id = serializers.IntegerField()
    distance_km = serializers.FloatField()
    estimated_arrival = serializers.CharField()
    rating = serializers.FloatField(allow_null=True)
    location = PointSerializer()


class NearbyDriversResponseSerializer(serializers.Serializer):
    drivers = DriverSummarySerializer(many=True)
    total_found = serializers.IntegerField()
    search_radius = serializers.FloatField()


class CalculateDistanceRequestSerializer(serializers.Serializer):
    origin = PointSerializer()
    destination = PointSerializer()


class CalculateDistanceResponseSerializer(serializers.Serializer):
    distance_km = serializers.FloatField()
    estimated_time = serializers.CharField()
    route_found = serializers.BooleanField()


class ReverseGeocodeQuerySerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    lng = serializers.FloatField(min_value=-180.0, max_value=180.0)


class ReverseGeocodeResponseSerializer(serializers.Serializer):
    address = serializers.CharField()
    cached = serializers.BooleanField()


class BatchDistanceItemSerializer(serializers.Serializer):
    origin = PointSerializer()
    destination = PointSerializer()


class BatchReverseItemSerializer(serializers.Serializer):
    point = PointSerializer()


class BatchProcessRequestSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["distance", "reverse_geocode"])
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)


class BatchProcessDistanceResultSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    distance_km = serializers.FloatField()
    minutes = serializers.FloatField()
    route_found = serializers.BooleanField()


class BatchProcessReverseResultSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    address = serializers.CharField()
    cached = serializers.BooleanField()


class UpdateDriverLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    lng = serializers.FloatField(min_value=-180.0, max_value=180.0)
    speed_kmh = serializers.FloatField(min_value=0.0, required=False, default=0.0)
    heading = serializers.FloatField(min_value=0.0, max_value=359.0, required=False, allow_null=True)
    accuracy_m = serializers.FloatField(min_value=0.0, required=False, allow_null=True)


class CurrentDriverLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    is_online = serializers.BooleanField()
    speed_kmh = serializers.FloatField()
    heading = serializers.FloatField(allow_null=True)
    accuracy_m = serializers.FloatField(allow_null=True)
    updated_at = serializers.DateTimeField()
