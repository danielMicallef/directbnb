from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.builder.models import (
    ThemeChoices,
    ColorSchemeChoices,
    Website,
    RegistrationOptions,
    LeadRegistration,
)
from apps.builder.utils import is_email_blacklisted
from apps.properties.tasks import BNBUser


class ThemeChoicesSerializer(serializers.ModelSerializer):
    """Serializer for theme choices"""

    class Meta:
        model = ThemeChoices
        fields = ("id", "name", "icon_name", "created_at", "preview_link", "updated_at")
        read_only_fields = ("id", "created_at", "preview_link", "updated_at")


class ColorSchemeChoicesSerializer(serializers.ModelSerializer):
    """Serializer for color scheme choices"""

    class Meta:
        model = ColorSchemeChoices
        fields = ("id", "name", "theme_colors", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_theme_colors(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Theme colors must be a list.")

        valid_names = {
            "base",
            "primary",
            "secondary",
            "accent",
            "neutral",
            "info",
            "success",
            "warning",
            "error",
        }

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Each item in theme colors must be a dictionary."
                )
            if "name" not in item or "value" not in item:
                raise serializers.ValidationError(
                    "Each color item must have a 'name' and 'value'."
                )
            if item["name"] not in valid_names:
                raise serializers.ValidationError(f"Invalid color name: {item['name']}")
        return value


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for website with nested theme and color scheme details"""

    theme_detail = ThemeChoicesSerializer(source="theme", read_only=True)
    color_scheme_detail = ColorSchemeChoicesSerializer(
        source="color_scheme", read_only=True
    )

    class Meta:
        model = Website
        fields = (
            "id",
            "theme",
            "theme_detail",
            "color_scheme",
            "color_scheme_detail",
            "airbnb_listing_url",
            "booking_listing_url",
            "domain_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_airbnb_listing_url(self, value):
        """Validate that airbnb URL contains airbnb.com"""
        if value and "airbnb.com" not in value.lower():
            raise serializers.ValidationError(
                "Please provide a valid Airbnb listing URL"
            )
        return value

    def validate_booking_listing_url(self, value):
        """Validate that booking URL contains booking.com"""
        if value and "booking.com" not in value.lower():
            raise serializers.ValidationError(
                "Please provide a valid Booking.com listing URL"
            )
        return value


class WebsiteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating websites"""

    class Meta:
        model = Website
        fields = (
            "theme",
            "color_scheme",
            "airbnb_listing_url",
            "booking_listing_url",
            "domain_name",
        )

    def validate_airbnb_listing_url(self, value):
        """Validate that airbnb URL contains airbnb.com"""
        if value and "airbnb.com" not in value.lower():
            raise serializers.ValidationError(
                "Please provide a valid Airbnb listing URL"
            )
        return value

    def validate_booking_listing_url(self, value):
        """Validate that booking URL contains booking.com"""
        if value and "booking.com" not in value.lower():
            raise serializers.ValidationError(
                "Please provide a valid Booking.com listing URL"
            )
        return value


class RegistrationOptionsSerializer(serializers.ModelSerializer):
    """Serializer for RegistrationOptions"""

    class Meta:
        model = RegistrationOptions
        fields = (
            "id",
            "lead_registration",
            "promotion",
            "package",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LeadRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for LeadRegistration with nested RegistrationOptions"""

    registration_options = RegistrationOptionsSerializer(many=True, read_only=True)
    listing_urls = serializers.ListField(
        child=serializers.URLField(), allow_empty=True, allow_null=True
    )

    # Honey Pot Field
    confirm_email = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    class Meta:
        model = LeadRegistration
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "theme",
            "color_scheme",
            "listing_urls",
            "domain_name",
            "registration_options",
            "created_at",
            "updated_at",
            "confirm_email",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "email": {"write_only": True},
        }

    def validate_email(self, value):
        """
        Custom email validation to allow updates to the same email
        """
        value = value.strip().lower()
        # Allow update on the same instance
        if self.instance and self.instance.email == value:
            return value

        if is_email_blacklisted(value):
            raise serializers.ValidationError(
                _(
                    "This email domain has been blacklisted. Please use a different email address."
                )
            )

        # Check if email already exists for new instances
        if BNBUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("A user with this email already exists.")
            )

        return value

    def validate_confirm_email(self, value):
        # Honey Pot Field. Should be empty
        if value.strip():
            raise serializers.ValidationError(
                _("Invalid submission.")
            )
        return value

    def validate(self, data):
        data.pop("confirm_email", None)
        return data