from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import PropertyViewSet
from .views import PropertyListView, PropertyDetailView, PropertyUpdateView

app_name = "properties"

# REST API Router
router = DefaultRouter()
router.register(r"", PropertyViewSet, basename="property")

# URL Patterns
urlpatterns = [
    # API URLs (for GET requests and REST operations)
    path("api/", include(router.urls)),
    # Form-based URLs (for logged-in users to view/edit properties)
    path("", PropertyListView.as_view(), name="property-list"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="property-detail"),
    path("<int:pk>/edit/", PropertyUpdateView.as_view(), name="property-update"),
]
