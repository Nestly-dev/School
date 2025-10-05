from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # your existing APIs
    path("api/users/", include("users.urls")),
    path("api/locations/", include("locations.urls")),
    path("api/rides/", include("rides.urls")),

    # OpenAPI schema + docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    path("api/", include("authx.urls", namespace="authx")),
    path('api/auth/', include('auth_app.urls_auth')),
    
]
