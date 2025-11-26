import json
import stripe

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from loguru import logger
from pydantic_core._pydantic_core import ValidationError
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from stripe import SignatureVerificationError

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import datetime

from apps.builder.models import (
    ThemeChoices,
    ColorSchemeChoices,
    Website,
    LeadRegistration,
    RegistrationOptions,
    Package,
    StripeWebhookPayload,
)
from apps.builder.permissions import IsLeadRegistrationNotCompleted
from apps.builder.schemas import StripeEvent, StripeEventType
from apps.builder.serializers import (
    ThemeChoicesSerializer,
    ColorSchemeChoicesSerializer,
    WebsiteSerializer,
    WebsiteCreateUpdateSerializer,
    LeadRegistrationSerializer,
    RegistrationOptionsSerializer,
    PackageSerializer,
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["email"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ("updated_at", "created_at")

    def get_permissions(self):
        if self.action in ["create", "partial_update", "list"]:
            return [AllowAny()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "completed_at" in request.data and instance.completed_at is None:
            checkout_session = instance.create_checkout_session()
            self.checkout_url = checkout_session.url

        return super().update(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self, "checkout_url"):
            context["checkout_url"] = self.checkout_url
        return context


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

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsLeadRegistrationNotCompleted()]
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Optionally filter by lead_registration ID
        """
        queryset = super().get_queryset()
        lead_registration = self.request.query_params.get("lead_registration", None)
        if lead_registration:
            queryset = queryset.filter(lead_registration_id=lead_registration)
        return queryset


class StripeWebhookView(APIView):
    """
    Stripe webhook view to handle checkout session completion.
    """

    permission_classes = [AllowAny]

    @staticmethod
    def handle_checkout_session_completed(
        stripe_event: StripeEvent,
    ) -> tuple[bool, str]:
        lead_registration_id = stripe_event.get_lead_registration_id()
        try:
            lead_registration = LeadRegistration.objects.get(id=lead_registration_id)

            # Update all registration options with payment timestamp
            lead_registration.registration_options.update(paid_at=datetime.now())
            logger.info(f"Lead registration {lead_registration_id} payment recorded")

            # Create user account from lead registration
            user, user_created = lead_registration.create_user_from_lead()
            if user_created:
                logger.info(
                    f"Created new user {user.email} from lead registration {lead_registration_id}"
                )
            else:
                logger.info(
                    f"User {user.email} already exists for lead registration {lead_registration_id}"
                )
        except LeadRegistration.DoesNotExist:
            logger.error(f"Lead registration {lead_registration_id} not found")
            return False, "Lead registration not found"
        except Exception as e:
            logger.error(
                f"Error handling checkout session completed for {lead_registration_id}: {e}"
            )
            return (
                False,
                f"Error handling checkout session completed for {lead_registration_id}",
            )

        # Send payment confirmation email with email verification link
        try:
            lead_registration.send_payment_confirmation_email()
            logger.info(
                f"Payment confirmation email sent to {user.email} for lead {lead_registration_id}"
            )
        except Exception as email_error:
            # Don't fail the webhook if email fails - payment was still processed
            # Todo: Queue this for retry using Celery
            logger.error(
                f"Failed to send payment confirmation email to {user.email}: {email_error}"
            )

        return True, "User created."

    @staticmethod
    def validate_webhook_request(request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        if not sig_header:
            return False, {"error": "No Stripe signature provided"}

        try:
            event = stripe.Webhook.construct_event(
                request.body, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.info(f"Stripe webhook validation failed: {e}")
            data = {"error": "Invalid payload."}
            return False, data
        except SignatureVerificationError as e:
            logger.info(f"Stripe webhook signature verification failed: {e}")
            data = {"error": "Invalid signature."}
            return False, data

        return True, event

    def get_event_handler_map(self, event_type: StripeEvent):
        event_handler_map = {
            StripeEventType.CHECKOUT_COMPLETED: self.handle_checkout_session_completed,
        }
        return event_handler_map.get(event_type.type, self.default_handler)

    def default_handler(self, event_type: StripeEvent) -> tuple[bool, str]:
        logger.info(
            f"Unprocessed Stripe webhook event: {event_type.type}. Data: {event_type.model_dump()}"
        )
        return True, f"Unprocessed Stripe webhook event {event_type.type}"

    def post(self, request, *args, **kwargs):
        is_valid, validation_data = self.validate_webhook_request(request)
        if not is_valid:
            return Response(validation_data, status=status.HTTP_400_BAD_REQUEST)

        payload = request.body
        json_data = json.loads(payload.decode("utf-8"))
        stripe_webhook = StripeWebhookPayload.objects.create(
            payload=json_data, processed_successfully=False
        )
        try:
            stripe_event = StripeEvent.model_validate_json(payload)
        except ValidationError as e:
            logger.error("Stripe webhook validation failed: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        lead_registration_id = stripe_event.get_lead_registration_id()
        lead_registration = LeadRegistration.objects.filter(
            id=lead_registration_id
        ).first()
        stripe_webhook.lead_registration = lead_registration
        event_handler = self.get_event_handler_map(stripe_event)
        updated, reason = False, ""
        try:
            updated, reason = event_handler(stripe_event)
            stripe_webhook.completed_at = datetime.now()
            stripe_webhook.processed_successfully = updated
        except Exception as e:
            logger.error(
                f"Unable to process Stripe webhook event. Data: {stripe_event.model_dump()}. Error: {e}"
            )

        stripe_webhook.save()
        ret_status = status.HTTP_200_OK if updated else status.HTTP_400_BAD_REQUEST
        return Response(status=ret_status, data={"reason": reason})


class PackageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API view to list all packages grouped by label (Builder, Hosting, Add-on)
    """

    queryset = Package.objects.all().order_by("label", "amount")
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Returns packages grouped by their label.
        Response format:
        {
            "Builder": [...],
            "Hosting": [...],
            "Add-on": [...]
        }
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Group packages by label
        grouped_packages = {}
        for package_data in serializer.data:
            label = package_data.get("label_display", "Unknown")
            if label not in grouped_packages:
                grouped_packages[label] = []
            grouped_packages[label].append(package_data)

        return Response(grouped_packages, status=status.HTTP_200_OK)
