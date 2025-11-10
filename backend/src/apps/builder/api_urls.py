from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.builder import api_views

app_name = "builder_api"

# Create router for ViewSets
router = DefaultRouter()
router.register(r"themes", api_views.ThemeChoicesViewSet, basename="theme")
router.register(
    r"color-schemes", api_views.ColorSchemeChoicesViewSet, basename="color-scheme"
)
router.register(r"websites", api_views.WebsiteViewSet, basename="website")
router.register(
    r"lead-registrations",
    api_views.LeadRegistrationViewSet,
    basename="lead-registration",
)
router.register(
    r"registration-options",
    api_views.RegistrationOptionsViewSet,
    basename="registration-options",
)
router.register(r"packages", api_views.PackageViewSet, basename="package")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "stripe-webhook/",
        api_views.StripeWebhookView.as_view(),
        name="stripe-webhook",
    ),
]
