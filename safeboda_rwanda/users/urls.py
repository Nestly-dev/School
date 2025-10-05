from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    RegistrationView,
    ProfileView,
    DistrictsView,
    PhoneValidationView,
    NationalIDValidationView,
    UsersListView,
    DriversListView,
)

app_name = "users"

urlpatterns = [
    # auth
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # profile
    path("me/", ProfileView.as_view(), name="me"),

    # helpers
    path("districts/", DistrictsView.as_view(), name="districts"),
    path("validate/phone/", PhoneValidationView.as_view(), name="validate_phone"),
    path("validate/national-id/", NationalIDValidationView.as_view(), name="validate_national_id"),

    # lists
    path("", UsersListView.as_view(), name="users_list"),
    path("drivers/", DriversListView.as_view(), name="drivers_list"),
]
