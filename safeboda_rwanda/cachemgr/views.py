from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from common.cache import CACHE_METRICS, clear_cache_keys


@extend_schema(
    tags=["Cache"],
    summary="Cache system health",
    responses={200: dict},
)
class CacheHealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        snap = CACHE_METRICS.snapshot()
        return Response(
            {"status": "ok", "cache_hit_ratio": snap["cache_hit_ratio"]},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Cache"],
    summary="Cache performance stats",
    responses={200: dict},
)
class CacheStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(CACHE_METRICS.snapshot(), status=status.HTTP_200_OK)


@extend_schema(
    tags=["Cache"],
    summary="Clear caches (admin only)",
    request=dict,
    responses={200: dict},
)
class CacheClearView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        prefix = (request.data or {}).get("prefix")
        clear_cache_keys(prefix=prefix)
        return Response({"detail": "cache clear requested", "prefix": prefix}, status=status.HTTP_200_OK)
