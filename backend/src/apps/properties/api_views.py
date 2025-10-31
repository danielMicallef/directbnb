from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Property
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a property to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the property
        return obj.owner == request.user


class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing property instances.

    Provides standard CRUD operations:
    - list: GET /api/properties/
    - retrieve: GET /api/properties/{id}/
    - create: POST /api/properties/
    - update: PUT /api/properties/{id}/
    - partial_update: PATCH /api/properties/{id}/
    - destroy: DELETE /api/properties/{id}/

    Additional actions:
    - my_properties: GET /api/properties/my_properties/ - Get all properties for the logged-in user
    """

    queryset = Property.objects.select_related(
        "owner",
        "coordinates",
        "rating",
        "house_rules",
        "host",
        "sub_description",
    ).prefetch_related(
        "amenities",
        "amenities__values",
        "images",
        "location_descriptions",
        "highlights",
        "co_hosts",
        "house_rules__general",
        "house_rules__general__values",
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action == "list":
            return PropertyListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer

    def get_queryset(self):
        """
        Optionally filter properties by owner.
        """
        queryset = super().get_queryset()

        # Filter by owner if owner_id query param is provided
        owner_id = self.request.query_params.get("owner_id")
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        return queryset

    def perform_create(self, serializer):
        """
        Set the owner to the current user when creating a property.
        """
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_properties(self, request):
        """
        Get all properties for the logged-in user.
        """
        properties = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)
