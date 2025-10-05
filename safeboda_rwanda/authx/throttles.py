from rest_framework.throttling import SimpleRateThrottle

class IPBurstThrottle(SimpleRateThrottle):
    scope = "ip_burst"
    def get_cache_key(self, request, view):
        return self.get_ident(request)

class IPSustainedThrottle(SimpleRateThrottle):
    scope = "ip_sustained"
    def get_cache_key(self, request, view):
        return self.get_ident(request)
