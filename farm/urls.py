from django.urls import path
from .views import ProduceListView

urlpatterns = [
    path('', ProduceListView.as_view(), name='produce-list'),
]
