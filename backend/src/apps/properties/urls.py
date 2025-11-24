from django.urls import path

from .views import PropertyListView, PropertyDetailView, PropertyUpdateView

app_name = "properties"

# URL Patterns
urlpatterns = [
    # Form-based URLs (for logged-in users to view/edit properties)
    path("", PropertyListView.as_view(), name="property-list"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="property-detail"),
    path("<int:pk>/edit/", PropertyUpdateView.as_view(), name="property-update"),
]
