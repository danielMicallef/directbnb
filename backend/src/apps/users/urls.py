from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify/<uuid:token>/", views.verify_email, name="verify_email"),
]