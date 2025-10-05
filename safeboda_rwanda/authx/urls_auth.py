from django.urls import path
from .views_auth import SessionLoginView, SessionLogoutView

urlpatterns = [
    path('session/login/', SessionLoginView.as_view(), name='session_login'),
    path('session/logout/', SessionLogoutView.as_view(), name='session_logout'),
]
