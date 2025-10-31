from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/<uuid:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.ResendVerificationEmailView.as_view(), name="resend_verification"),
    path("", views.HomeView.as_view(), name="home"),
]