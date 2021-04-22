from django.urls import path

from src.apis.views import (
    UserSignupView,
    UserLoginView,
    RefreshTokenView,
    EmailVerificationView,
    SendLoginOTPView,
    ResetPasswordView,
    EmailResetPasswordView,
)
from src.apis.views.user import (
    UserProfileView,
    UserChangePasswordView,
    UserListView,
)

urlpatterns = [
    path("auth/signup/", UserSignupView.as_view(), name="user-signup"),
    path("auth/login/", UserLoginView.as_view(), name="user-login"),
    path("auth/refresh-token/", RefreshTokenView.as_view(), name="auth-refresh-token"),
    path(
        "auth/verify-email/",
        EmailVerificationView.as_view(),
        name="email-verification",
    ),
    path("auth/send-otp/", SendLoginOTPView.as_view(), name="send-login-otp"),
    path(
        "auth/email/reset-password/",
        EmailResetPasswordView.as_view(),
        name="reset-password-eamil",
    ),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("me/profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "me/change-password/",
        UserChangePasswordView.as_view(),
        name="user-reset-password",
    ),
    path("me/users/", UserListView.as_view(), name="user-list"),
    path("me/users/<int:pk>/", UserListView.as_view(), name="user-detail"),
]
