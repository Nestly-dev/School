# locations/views.py
import math
from datetime import timedelta

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Count
from django.db.models.functions import Round
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.cache import cached_response_or_build, set_cache_headers
from .models import DriverLocation, LocationPing
from .permissions import IsDriverOrAdmin
from .serializers import (
    BatchProcessRequestSerializer,
    CalculateDistanceRequestSerializer,
    CalculateDistanceResponseSerializer,
    CurrentDriverLocationSerializer,
    NearbyDriversRequestSerializer,
    NearbyDriversResponseSerializer,
    ReverseGeocodeQuerySerializer,
    ReverseGeocodeResponseSerializer,
    UpdateDriverLocationSerializer,
)
from .services import (
    AsyncLocationService,
    arrival_text,
    estimate_eta_minutes,
    haversine_km,
)


def driver_base_queryset():
    User = get_user_model()
    try:
        User._meta.get_field("user_type")
        return User.objects.filter(user_type="driver")
    except FieldDoesNotExist:
        # If you classify drivers via Groups, you can tighten this here.
        return User.objects.all()


@extend_schema(
    tags=["Locations"],
    request=NearbyDriversRequestSerializer,
    responses={200: NearbyDriversResponseSerializer},
    summary="Find nearby drivers within a radius (cached 60s)",
)
class NearbyDriversView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = NearbyDriversRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        lat = ser.validated_data["lat"]
        lng = ser.validated_data["lng"]
        radius_km = ser.validated_data["radius_km"]
        limit = ser.validated_data["limit"]

        def build():
            # prune by bounding box
            lat_deg = radius_km / 111.0
            lng_deg = radius_km / max(0.00001, (111.0 * abs(math.cos(math.radians(lat))) or 1e-6))
            candidates = (
                DriverLocation.objects.select_related("driver")
                .filter(
                    is_online=True,
                    lat__gte=lat - lat_deg,
                    lat__lte=lat + lat_deg,
                    lng__gte=lng - lng_deg,
                    lng__lte=lng + lng_deg,
                )
            )
            candidates = candidates.filter(driver__in=driver_base_queryset())

            results = []
            for dl in candidates:
                d_km = haversine_km(lat, lng, dl.lat, dl.lng)
                if d_km <= radius_km:
                    eta_min = estimate_eta_minutes(d_km)
                    rating = getattr(dl.driver, "rating", 5.0)
                    results.append(
                        {
                            "driver_id": dl.driver_id,
                            "distance_km": round(d_km, 3),
                            "estimated_arrival": arrival_text(eta_min),
                            "rating": float(rating) if rating is not None else None,
                            "location": {"lat": dl.lat, "lng": dl.lng},
                        }
                    )
            results.sort(key=lambda x: x["distance_km"])
            payload = {"drivers": results[:limit], "total_found": len(results), "search_radius": radius_km}
            resp = Response(payload, status=status.HTTP_200_OK)
            # also set explicit cache headers (will be overwritten by wrapper)
            set_cache_headers(resp, ttl=60, status_txt="MISS", cache_key="N/A")
            return resp

        # cache whole response for 60s (popular endpoint)
        return cached_response_or_build(
            request,
            name="locations.nearby",
            ttl=60,
            build_func=build,
            body_fields=ser.validated_data,
        )


@extend_schema(
    tags=["Locations"],
    request=CalculateDistanceRequestSerializer,
    responses={200: CalculateDistanceResponseSerializer},
    summary="Calculate distance & ETA between two points (route cached 5m)",
)
class CalculateDistanceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = CalculateDistanceRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        origin = (ser.validated_data["origin"]["lat"], ser.validated_data["origin"]["lng"])
        dest = (ser.validated_data["destination"]["lat"], ser.validated_data["destination"]["lng"])

        distance_km, minutes, route_found = async_to_sync(
            AsyncLocationService.fetch_route_distance_time
        )(origin, dest)

        resp = Response(
            {
                "distance_km": round(distance_km, 3),
                "estimated_time": arrival_text(minutes),
                "route_found": route_found,
            },
            status=status.HTTP_200_OK,
        )
        # downstream route call already cached; still add response cache headers guidance
        set_cache_headers(resp, ttl=300, status_txt="BYPASS", cache_key="route-cache-internal")
        return resp


@extend_schema(
    tags=["Locations"],
    parameters=[
        OpenApiParameter(name="lat", required=True, type=float, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="lng", required=True, type=float, location=OpenApiParameter.QUERY),
    ],
    responses={200: ReverseGeocodeResponseSerializer},
    summary="Reverse geocode coordinates (cached 1h)",
)
class ReverseGeocodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ser = ReverseGeocodeQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        lat = ser.validated_data["lat"]
        lng = ser.validated_data["lng"]

        def build():
            address, cached = async_to_sync(AsyncLocationService.reverse_geocode)(lat, lng)
            resp = Response({"address": address, "cached": cached}, status=status.HTTP_200_OK)
            set_cache_headers(resp, ttl=3600, status_txt="MISS", cache_key="N/A")
            return resp

        return cached_response_or_build(
            request,
            name="locations.reverse",
            ttl=3600,
            build_func=build,
            body_fields={"lat": lat, "lng": lng},
        )


@extend_schema(
    tags=["Locations"],
    request=dict,
    responses={200: dict},
    summary="Batch process distances or reverse geocodes (concurrent)",
)
class BatchProcessView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from .serializers import BatchProcessRequestSerializer  # local import to avoid circular
        ser = BatchProcessRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        mode = ser.validated_data["mode"]
        items = ser.validated_data["items"]

        if mode == "distance":
            pairs = []
            for i, it in enumerate(items):
                origin = it.get("origin")
                dest = it.get("destination")
                if not origin or not dest:
                    return Response({"detail": f"items[{i}] must include origin and destination"}, status=400)
                pairs.append(((origin["lat"], origin["lng"]), (dest["lat"], dest["lng"])))
            results = async_to_sync(AsyncLocationService.batch_distance)(pairs)
            payload = []
            for idx, (km, mins, found) in enumerate(results):
                payload.append({"index": idx, "distance_km": round(km, 3), "minutes": round(mins, 1), "route_found": found})
            return Response({"mode": "distance", "results": payload}, status=200)

        elif mode == "reverse_geocode":
            points = []
            for i, it in enumerate(items):
                p = it.get("point")
                if not p:
                    return Response({"detail": f"items[{i}] must include point"}, status=400)
                points.append((p["lat"], p["lng"]))
            results = async_to_sync(AsyncLocationService.batch_reverse)(points)
            payload = [{"index": i, "address": addr, "cached": cached} for i, (addr, cached) in enumerate(results)]
            return Response({"mode": "reverse_geocode", "results": payload}, status=200)

        return Response({"detail": "Unsupported mode"}, status=400)


@extend_schema(
    tags=["Locations"],
    request=UpdateDriverLocationSerializer,
    responses={200: dict},
    summary="Update driver location (auth driver)",
)
class DriverUpdateLocationView(APIView):
    permission_classes = [IsAuthenticated, IsDriverOrAdmin]

    def put(self, request):
        ser = UpdateDriverLocationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        lat = ser.validated_data["lat"]
        lng = ser.validated_data["lng"]
        speed_kmh = ser.validated_data.get("speed_kmh", 0.0)
        heading = ser.validated_data.get("heading")
        accuracy_m = ser.validated_data.get("accuracy_m")

        dl, _created = DriverLocation.objects.update_or_create(
            driver=request.user,
            defaults=dict(
                lat=lat,
                lng=lng,
                speed_kmh=speed_kmh,
                heading=heading,
                accuracy_m=accuracy_m,
                is_online=True,
            ),
        )
        LocationPing.objects.create(
            driver=request.user,
            lat=lat,
            lng=lng,
            speed_kmh=speed_kmh,
            heading=heading,
            accuracy_m=accuracy_m,
        )

        resp = Response({"detail": "Location updated", "driver_id": request.user.id, "lat": lat, "lng": lng}, status=200)
        set_cache_headers(resp, ttl=0, status_txt="BYPASS", cache_key="nocache-mutate")
        return resp


@extend_schema(
    tags=["Locations"],
    responses={200: CurrentDriverLocationSerializer},
    summary="Get current driver location (auth driver)",
)
class DriverCurrentLocationView(APIView):
    permission_classes = [IsAuthenticated, IsDriverOrAdmin]

    def get(self, request):
        try:
            dl = request.user.driver_location
        except DriverLocation.DoesNotExist:
            return Response({"detail": "No location found"}, status=404)
        resp = Response(
            {
                "lat": dl.lat,
                "lng": dl.lng,
                "is_online": dl.is_online,
                "speed_kmh": dl.speed_kmh,
                "heading": dl.heading,
                "accuracy_m": dl.accuracy_m,
                "updated_at": dl.updated_at,
            },
            status=200,
        )
        set_cache_headers(resp, ttl=15, status_txt="BYPASS", cache_key="short-lived")
        return resp


@extend_schema(
    tags=["Locations"],
    parameters=[OpenApiParameter(name="limit", type=int, location=OpenApiParameter.QUERY, required=False)],
    summary="Popular locations (clustered pings, last 24h)",
    responses={200: dict},
)
class PopularLocationsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = int(request.GET.get("limit", "10"))
        except Exception:
            limit = 10

        since = timezone.now() - timedelta(days=1)
        # cluster by rounded lat/lng (3 decimals ~ ~110m)
        qs = (
            LocationPing.objects.filter(created_at__gte=since)
            .annotate(lat_r=Round("lat", 3), lng_r=Round("lng", 3))
            .values("lat_r", "lng_r")
            .annotate(count=Count("id"))
            .order_by("-count")[:limit]
        )
        results = [{"lat": float(x["lat_r"]), "lng": float(x["lng_r"]), "count": x["count"]} for x in qs]
        resp = Response({"results": results, "window_hours": 24}, status=200)
        set_cache_headers(resp, ttl=120, status_txt="BYPASS", cache_key="popular-24h")
        return resp
