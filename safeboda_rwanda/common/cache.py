# common/cache.py
import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse


# ----------------- Metrics -----------------

@dataclass
class CacheMetrics:
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    endpoint_counts: Dict[str, int] = field(default_factory=dict)
    endpoint_hits: Dict[str, int] = field(default_factory=dict)
    endpoint_misses: Dict[str, int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, key: str, hit: bool):
        with self.lock:
            self.total_requests += 1
            self.endpoint_counts[key] = self.endpoint_counts.get(key, 0) + 1
            if hit:
                self.hits += 1
                self.endpoint_hits[key] = self.endpoint_hits.get(key, 0) + 1
            else:
                self.misses += 1
                self.endpoint_misses[key] = self.endpoint_misses.get(key, 0) + 1

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            ratio = (self.hits / self.total_requests) if self.total_requests else 0.0
            most_cached = sorted(
                self.endpoint_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
            return {
                "cache_hit_ratio": round(ratio, 3),
                "total_requests": self.total_requests,
                "cache_hits": self.hits,
                "cache_misses": self.misses,
                "most_cached_endpoints": [k for k, _ in most_cached],
                "endpoint_counts": dict(self.endpoint_counts),
                "endpoint_hits": dict(self.endpoint_hits),
                "endpoint_misses": dict(self.endpoint_misses),
            }


CACHE_METRICS = CacheMetrics()


# ----------------- Small TTL cache for in-process (used by locations too) -----------------

class TTLCache:
    def __init__(self, name: str, default_ttl: int = 300) -> None:
        self.name = name
        self.default_ttl = default_ttl
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Tuple[bool, Optional[Any]]:
        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if not item:
                CACHE_METRICS.record(f"{self.name}:{key}", False)
                return False, None
            expires_at, value = item
            if expires_at < now:
                self._store.pop(key, None)
                CACHE_METRICS.record(f"{self.name}:{key}", False)
                return False, None
            CACHE_METRICS.record(f"{self.name}:{key}", True)
            return True, value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        with self._lock:
            self._store[key] = (time.time() + ttl, value)

    def clear(self, prefix: Optional[str] = None):
        with self._lock:
            if prefix is None:
                self._store.clear()
            else:
                for k in list(self._store.keys()):
                    if k.startswith(prefix):
                        self._store.pop(k, None)


# ----------------- Response caching helpers -----------------

def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def make_cache_key_for_request(
    request: HttpRequest,
    *,
    name: str,
    body_fields: Optional[Dict[str, Any]] = None,
    extra: Optional[str] = None,
) -> str:
    """
    Builds a stable cache key based on path + selected body/query fields.
    Use for POST endpoints where body determines the response (e.g., drivers/nearby).
    """
    base = f"{name}:{request.path}"
    if request.method == "GET":
        q = request.GET.urlencode()
        base = f"{base}?{q}"
    else:
        if body_fields is None:
            try:
                payload = json.loads(request.body.decode() or "{}")
            except Exception:
                payload = {}
        else:
            payload = body_fields
        base = f"{base}:{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"
    if extra:
        base = f"{base}:{extra}"
    return f"resp:{_hash_bytes(base.encode())}"


def set_cache_headers(resp: HttpResponse, *, ttl: int, status_txt: str, cache_key: str):
    resp["Cache-Control"] = f"max-age={ttl}"
    resp["X-Cache-Status"] = status_txt  # HIT / MISS / BYPASS
    resp["X-Cache-Key"] = cache_key


def cached_response_or_build(
    request: HttpRequest,
    *,
    name: str,
    ttl: int,
    build_func: Callable[[], HttpResponse],
    body_fields: Optional[Dict[str, Any]] = None,
) -> HttpResponse:
    """
    Cache wrapper for whole responses (good for frequently-hit read endpoints).
    Uses Django's default cache (LocMem in your settings now).
    """
    cache_key = make_cache_key_for_request(request, name=name, body_fields=body_fields)
    CACHE_METRICS.record(name, False)  # will correct to HIT below if hit

    cached = cache.get(cache_key)
    if cached is not None:
        resp: HttpResponse = cached
        set_cache_headers(resp, ttl=ttl, status_txt="HIT", cache_key=cache_key)
        CACHE_METRICS.record(name, True)
        return resp

    resp = build_func()
    cache.set(cache_key, resp, ttl)
    set_cache_headers(resp, ttl=ttl, status_txt="MISS", cache_key=cache_key)
    return resp


def clear_cache_keys(prefix: Optional[str] = None):
    """
    Clears Django cache keys by prefix (best-effort; LocMem doesn't support wildcard iteration).
    For our assignment, we clear known keys by strategy, or simply increment a 'version' namespace.
    """
    # Simple strategy: bump a namespace version number.
    # (Keeping it simple due to backend differences; real Redis would use SCAN + DEL.)
    version = cache.get("global_version", 1)
    cache.set("global_version", version + 1, None)
