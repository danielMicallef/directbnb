from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "set-initial-password/<uidb64>/<token>/",
        views.SetInitialPasswordView.as_view(),
        name="set_initial_password",
    ),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/<uuid:token>/", views.verify_email, name="verify_email"),
    path(
        "resend-verification/",
        views.ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
    path(
        "password-reset/",
        views.BnbPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.BnbPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.BnbPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.BnbPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("", views.HomeView.as_view(), name="home"),
]
