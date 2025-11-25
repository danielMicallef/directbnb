from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Property, TouristAttraction, Article
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
    TouristAttractionSerializer,
    ArticleSerializer,
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
        "attractions",
        "articles",
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

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_properties(self, request):
        """
        Get all properties for the logged-in user.
        """
        properties = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)


class TouristAttractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing tourist attractions.
    
    Provides read-only operations:
    - list: GET /api/attractions/
    - retrieve: GET /api/attractions/{id}/
    
    Query params:
    - property_id: Filter attractions by property
    """
    queryset = TouristAttraction.objects.all()
    serializer_class = TouristAttractionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        property_id = self.request.query_params.get('property_id')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        return queryset.order_by('order', 'distance')


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing articles/blogs.
    
    Provides read-only operations:
    - list: GET /api/articles/
    - retrieve: GET /api/articles/{slug}/
    
    Query params:
    - property_id: Filter articles by property
    - tags: Filter by tags (comma-separated)
    """
    queryset = Article.objects.filter(published=True)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by property
        property_id = self.request.query_params.get('property_id')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            # Filter articles that contain ANY of the specified tags
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])
        
        return queryset
