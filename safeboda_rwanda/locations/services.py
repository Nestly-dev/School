# locations/services.py
import asyncio
import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

import aiohttp

from common.cache import TTLCache


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def estimate_eta_minutes(distance_km: float, avg_speed_kmh: float = 15.0) -> float:
    if avg_speed_kmh <= 0:
        return float("inf")
    return (distance_km / avg_speed_kmh) * 60.0


def arrival_text(minutes: float) -> str:
    if minutes == float("inf"):
        return "unavailable"
    if minutes < 1.0:
        return "under a minute"
    if minutes < 60:
        return f"{int(round(minutes))} minutes"
    hours = int(minutes // 60)
    mins = int(round(minutes % 60))
    if mins == 0:
        return f"{hours} hours"
    return f"{hours}h {mins}m"


# per-process caches + metrics
reverse_cache = TTLCache(name="reverse", default_ttl=3600)  # 1h
route_cache = TTLCache(name="route", default_ttl=300)       # 5m


class AsyncLocationService:
    OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/{o_lng},{o_lat};{d_lng},{d_lat}?overview=false"
    NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lng}"

    HEADERS = {
        "User-Agent": "SafeBoda-Rwanda-Student-Project/1.0",
        "Accept": "application/json",
    }

    @staticmethod
    async def fetch_route_distance_time(
        origin: Tuple[float, float], destination: Tuple[float, float]
    ) -> Tuple[float, float, bool]:
        o_lat, o_lng = origin
        d_lat, d_lng = destination
        cache_key = f"route:{round(o_lat,5)},{round(o_lng,5)}->{round(d_lat,5)},{round(d_lng,5)}"

        hit, cached = route_cache.get(cache_key)
        if hit:
            return cached

        url = AsyncLocationService.OSRM_ROUTE_URL.format(
            o_lng=o_lng, o_lat=o_lat, d_lng=d_lng, d_lat=d_lat
        )
        timeout = aiohttp.ClientTimeout(total=6)
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=AsyncLocationService.HEADERS) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        routes = data.get("routes") or []
                        if routes:
                            meters = routes[0].get("distance", 0.0)
                            seconds = routes[0].get("duration", 0.0)
                            km = meters / 1000.0
                            minutes = seconds / 60.0
                            result = (km, minutes, True)
                            route_cache.set(cache_key, result)
                            return result
        except Exception:
            pass

        km = haversine_km(o_lat, o_lng, d_lat, d_lng)
        minutes = estimate_eta_minutes(km)
        result = (km, minutes, False)
        route_cache.set(cache_key, result)
        return result

    @staticmethod
    async def reverse_geocode(lat: float, lng: float) -> Tuple[str, bool]:
        cache_key = f"rev:{round(lat,5)},{round(lng,5)}"
        hit, cached = reverse_cache.get(cache_key)
        if hit:
            return cached, True

        url = AsyncLocationService.NOMINATIM_REVERSE_URL.format(lat=lat, lng=lng)
        timeout = aiohttp.ClientTimeout(total=6)
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=AsyncLocationService.HEADERS) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        address = data.get("display_name") or "Unknown address"
                        reverse_cache.set(cache_key, address)
                        return address, False
        except Exception:
            pass
        address = f"({lat:.5f}, {lng:.5f})"
        reverse_cache.set(cache_key, address, ttl=60)
        return address, False

    @staticmethod
    async def batch_distance(pairs: Iterable[Tuple[Tuple[float, float], Tuple[float, float]]]):
        tasks = [AsyncLocationService.fetch_route_distance_time(a, b) for a, b in pairs]
        return await asyncio.gather(*tasks, return_exceptions=False)

    @staticmethod
    async def batch_reverse(points: Iterable[Tuple[float, float]]):
        tasks = [AsyncLocationService.reverse_geocode(lat, lng) for lat, lng in points]
        return await asyncio.gather(*tasks, return_exceptions=False)
