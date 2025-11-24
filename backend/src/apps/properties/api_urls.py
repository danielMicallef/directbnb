from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import PropertyViewSet

app_name = "properties_api"

# REST API Router
router = DefaultRouter()
router.register(r"", PropertyViewSet, basename="property")

urlpatterns = [
    path("", include(router.urls)),
]
