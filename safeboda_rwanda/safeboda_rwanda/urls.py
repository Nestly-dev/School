from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core APIs
    path("api/users/", include("users.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/rides/", include("rides.urls")),
    path("api/cache/", include("cachemgr.urls")),

    # Government Integration (Task 4)
    path("api/government/", include("government.urls", namespace="government")),

    # Analytics & Business Intelligence (Task 5)
    path("api/analytics/", include("analytics.urls", namespace="analytics")),

    # Monitoring & Production (Task 3)
    path("api/health/", include("monitoring.urls")),
    path("api/monitoring/", include("monitoring.urls")),
    path("api/admin/", include("monitoring.urls")),

    # OpenAPI schema + docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Authentication
    path("api/", include("authx.urls", namespace="authx")),
]