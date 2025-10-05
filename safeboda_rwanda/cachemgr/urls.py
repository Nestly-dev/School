from django.urls import path
from .views import CacheStatsView, CacheClearView, CacheHealthView

app_name = "cachemgr"

urlpatterns = [
    path("stats/", CacheStatsView.as_view(), name="stats"),
    path("clear/", CacheClearView.as_view(), name="clear"),
    path("health/", CacheHealthView.as_view(), name="health"),
]
