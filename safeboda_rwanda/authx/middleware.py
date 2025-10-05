from __future__ import annotations
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from .models import AuditLog

SENSITIVE_PATH_PREFIXES = (
    "/api/auth/", "/api/privacy/", "/api/rbac/", "/api/uas/",
)

class SecurityAuditMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            path = request.path or ""
            if any(path.startswith(p) for p in SENSITIVE_PATH_PREFIXES):
                AuditLog.objects.create(
                    user=getattr(request, "user", None) if getattr(request, "user", None).is_authenticated else None,
                    actor_ip=self._ip(request),
                    path=path,
                    method=request.method,
                    event="API_CALL",
                    detail={
                        "status_code": response.status_code,
                        "timestamp": now().isoformat(),
                    }
                )
        except Exception:
            pass
        return response

    def _ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
