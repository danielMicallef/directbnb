from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import PropertyViewSet, TouristAttractionViewSet, ArticleViewSet

app_name = "properties_api"

# REST API Router
router = DefaultRouter()
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"attractions", TouristAttractionViewSet, basename="attraction")
router.register(r"articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("", include(router.urls)),
]
