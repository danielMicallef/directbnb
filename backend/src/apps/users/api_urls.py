from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users import api_views

app_name = "users_api"

urlpatterns = [
    # Authentication endpoints
    path("register/", api_views.RegisterAPIView.as_view(), name="register"),
    path("login/", api_views.LoginAPIView.as_view(), name="login"),
    path("logout/", api_views.LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User management endpoints
    path("me/", api_views.CurrentUserAPIView.as_view(), name="current_user"),
    path(
        "change-password/",
        api_views.ChangePasswordAPIView.as_view(),
        name="change_password",
    ),
    # Email verification
    path(
        "resend-verification/",
        api_views.ResendVerificationAPIView.as_view(),
        name="resend_verification",
    ),
]
