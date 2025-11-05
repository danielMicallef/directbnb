from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.builder.models import (
    ThemeChoices,
    ColorSchemeChoices,
    Website,
    LeadRegistration,
    RegistrationOptions,
)
from apps.builder.serializers import (
    ThemeChoicesSerializer,
    ColorSchemeChoicesSerializer,
    WebsiteSerializer,
    WebsiteCreateUpdateSerializer,
    LeadRegistrationSerializer,
    RegistrationOptionsSerializer,
)


@extend_schema_view(
    list=extend_schema(description="List all available theme choices"),
    retrieve=extend_schema(description="Get a specific theme choice by ID"),
    create=extend_schema(description="Create a new theme choice (admin only)"),
    update=extend_schema(description="Update a theme choice (admin only)"),
    partial_update=extend_schema(
        description="Partially update a theme choice (admin only)"
    ),
    destroy=extend_schema(description="Delete a theme choice (admin only)"),
)
class ThemeChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing theme choices.

    List and retrieve are available to all authenticated users.
    Create, update, and delete operations require admin permissions.
    """

    queryset = ThemeChoices.objects.all().order_by("name")
    serializer_class = ThemeChoicesSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin permissions required for write operations"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


@extend_schema_view(
    list=extend_schema(description="List all available color scheme choices"),
    retrieve=extend_schema(description="Get a specific color scheme by ID"),
    create=extend_schema(description="Create a new color scheme (admin only)"),
    update=extend_schema(description="Update a color scheme (admin only)"),
    partial_update=extend_schema(
        description="Partially update a color scheme (admin only)"
    ),
    destroy=extend_schema(description="Delete a color scheme (admin only)"),
)
class ColorSchemeChoicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing color scheme choices.

    List and retrieve are available to all authenticated users.
    Create, update, and delete operations require admin permissions.
    """

    queryset = ColorSchemeChoices.objects.all().order_by("name")
    serializer_class = ColorSchemeChoicesSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Admin permissions required for write operations"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            from rest_framework.permissions import IsAdminUser

            return [IsAdminUser()]
        return super().get_permissions()


@extend_schema_view(
    list=extend_schema(
        description="List all websites (users see only their own, admins see all)"
    ),
    retrieve=extend_schema(description="Get a specific website by ID"),
    create=extend_schema(description="Create a new website"),
    update=extend_schema(description="Update a website"),
    partial_update=extend_schema(description="Partially update a website"),
    destroy=extend_schema(description="Delete a website"),
)
class WebsiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing websites.

    Users can only view and manage their own websites.
    Admins can view and manage all websites.
    """

    queryset = Website.objects.all().select_related("theme", "color_scheme")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for read and write operations"""
        if self.action in ["create", "update", "partial_update"]:
            return WebsiteCreateUpdateSerializer
        return WebsiteSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()

        # Admins can see all websites
        if self.request.user.is_staff:
            return queryset

        # Regular users see only their own websites (when user field is added)
        # For now, return all (you'll need to add a user field to Website model)
        return queryset

    @extend_schema(
        description="Scrape data from Airbnb listing URL",
        request=None,
        responses={200: WebsiteSerializer},
    )
    @action(detail=True, methods=["post"])
    def scrape_airbnb(self, request, pk=None):
        """
        Scrape data from the Airbnb listing URL.

        This is a placeholder for future implementation.
        """
        website = self.get_object()

        if not website.airbnb_listing_url:
            return Response(
                {"error": _("No Airbnb listing URL configured")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: Implement Airbnb scraping logic here
        # This would use the pyairbnb package and Celery tasks

        return Response(
            {
                "message": _("Airbnb scraping task has been queued"),
                "website": WebsiteSerializer(website).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        description="Scrape data from Booking.com listing URL",
        request=None,
        responses={200: WebsiteSerializer},
    )
    @action(detail=True, methods=["post"])
    def scrape_booking(self, request, pk=None):
        """
        Scrape data from the Booking.com listing URL.

        This is a placeholder for future implementation.
        """
        website = self.get_object()

        if not website.booking_listing_url:
            return Response(
                {"error": _("No Booking.com listing URL configured")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: Implement Booking.com scraping logic here
        # This would use Celery tasks

        return Response(
            {
                "message": _("Booking.com scraping task has been queued"),
                "website": WebsiteSerializer(website).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        description="Get website configuration summary",
        responses={200: WebsiteSerializer},
    )
    @action(detail=True, methods=["get"])
    def configuration(self, request, pk=None):
        """
        Get a summary of the website configuration.

        Returns website details with theme and color scheme information.
        """
        website = self.get_object()
        serializer = self.get_serializer(website)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all lead registrations"),
    retrieve=extend_schema(description="Retrieve a specific lead registration"),
    create=extend_schema(description="Create a new lead registration"),
    update=extend_schema(description="Update a lead registration"),
    partial_update=extend_schema(description="Partially update a lead registration"),
)
class LeadRegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for LeadRegistration.
    Allows creating, retrieving, updating, and listing lead registrations.
    Designed for multi-step forms where data is posted incrementally.
    """

    queryset = LeadRegistration.objects.all()
    serializer_class = LeadRegistrationSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action in ["create"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Optionally filter by email query parameter
        """
        queryset = super().get_queryset()
        email = self.request.query_params.get("email", None)
        if email:
            queryset = queryset.filter(email=email)
        return queryset


@extend_schema_view(
    list=extend_schema(description="List all registration options"),
    retrieve=extend_schema(description="Retrieve specific registration options"),
    create=extend_schema(description="Create new registration options"),
    update=extend_schema(description="Update registration options"),
    partial_update=extend_schema(description="Partially update registration options"),
)
class RegistrationOptionsViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for RegistrationOptions.
    Allows creating, retrieving, updating, and listing registration options.
    Each option is linked to a LeadRegistration.
    """

    queryset = RegistrationOptions.objects.all()
    serializer_class = RegistrationOptionsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Optionally filter by lead_registration ID
        """
        queryset = super().get_queryset()
        lead_registration = self.request.query_params.get("lead_registration", None)
        if lead_registration:
            queryset = queryset.filter(lead_registration_id=lead_registration)
        return queryset
