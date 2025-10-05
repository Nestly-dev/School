from django.urls import path
from .views_auth import (
    BasicAuthView, SessionLoginView, SessionLogoutView,
    AuthMethodsView, JWTTokenObtainPairView, JWTTokenRefreshView, JWTTokenVerifyView
)
from .views_uas import (
    UASRegisterView, UASVerifyPhoneView, UASVerifyEmailView,
    PasswordResetRequestView, PasswordResetConfirmView, UASAccountStatusView
)
from .views_privacy import (
    DataExportView, DataDeletionRequestView, AuditLogView,
    ConsentView, AnonymizeView, RetentionPolicyView
)
from .views_rbac import (
    RolesListView, AssignRoleView, PermissionsListView, AdminUsersView,
    GovernmentAccessRequestView, PermissionAuditView, CreateRoleView
)

app_name = "authx"

urlpatterns = [
    # Task 1 – Auth
    path("auth/basic/", BasicAuthView.as_view(), name="auth-basic"),
    path("auth/session/login/", SessionLoginView.as_view(), name="auth-session-login"),
    path("auth/session/logout/", SessionLogoutView.as_view(), name="auth-session-logout"),
    path("auth/jwt/token/", JWTTokenObtainPairView.as_view(), name="jwt-token"),
    path("auth/jwt/refresh/", JWTTokenRefreshView.as_view(), name="jwt-refresh"),
    path("auth/jwt/verify/", JWTTokenVerifyView.as_view(), name="jwt-verify"),
    path("auth/methods/", AuthMethodsView.as_view(), name="auth-methods"),

    # Task 2 – UAS
    path("uas/register/", UASRegisterView.as_view(), name="uas-register"),
    path("uas/verify-phone/", UASVerifyPhoneView.as_view(), name="uas-verify-phone"),
    path("uas/verify-email/", UASVerifyEmailView.as_view(), name="uas-verify-email"),
    path("uas/password-reset/", PasswordResetRequestView.as_view(), name="uas-password-reset"),
    path("uas/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="uas-password-reset-confirm"),
    path("uas/account/status/", UASAccountStatusView.as_view(), name="uas-account-status"),

    # Task 3 – Privacy
    path("privacy/data-export/", DataExportView.as_view(), name="privacy-export"),
    path("privacy/data-deletion/", DataDeletionRequestView.as_view(), name="privacy-delete"),
    path("privacy/audit-log/", AuditLogView.as_view(), name="privacy-audit"),
    path("privacy/consent/", ConsentView.as_view(), name="privacy-consent"),
    path("privacy/anonymize/", AnonymizeView.as_view(), name="privacy-anonymize"),
    path("privacy/retention-policy/", RetentionPolicyView.as_view(), name="privacy-retention"),

    # Task 4 – RBAC
    path("rbac/roles/", RolesListView.as_view(), name="rbac-roles"),
    path("rbac/assign-role/", AssignRoleView.as_view(), name="rbac-assign"),
    path("rbac/permissions/", PermissionsListView.as_view(), name="rbac-perms"),
    path("rbac/admin/users/", AdminUsersView.as_view(), name="rbac-admin-users"),
    path("rbac/government/access-request/", GovernmentAccessRequestView.as_view(), name="rbac-gov-access"),
    path("rbac/audit/permissions/", PermissionAuditView.as_view(), name="rbac-audit"),
    path("rbac/create-role/", CreateRoleView.as_view(), name="rbac-create-role"),
]
