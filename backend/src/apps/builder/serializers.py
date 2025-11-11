from decimal import Decimal

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.builder.models import (
    ThemeChoices,
    ColorSchemeChoices,
    Website,
    RegistrationOptions,
    LeadRegistration,
    Package,
    Promotion,
    Frequency,
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
        read_only_fields = ("id", "created_at", "updated_at", "paid_at")


class LeadRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for LeadRegistration with nested RegistrationOptions"""

    registration_options = RegistrationOptionsSerializer(many=True, read_only=True)
    listing_urls = serializers.ListField(
        child=serializers.URLField(), allow_empty=True, allow_null=True
    )
    checkout_url = serializers.SerializerMethodField()

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
            "extra_requirements",
            "completed_at",
            "checkout_url",
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
            site_url = settings.SITE_URL
            raise serializers.ValidationError(
                _(f"A user with this email already exists. Login to your portal on {site_url}."),
            )
        return value

    def validate_confirm_email(self, value):
        # Honey Pot Field. Should be empty
        if value.strip():
            raise serializers.ValidationError(_("Invalid submission."))
        return value

    def validate(self, data):
        data.pop("confirm_email", None)
        return data

    def get_checkout_url(self, obj):
        return self.context.get("checkout_url")


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for Promotion model"""

    class Meta:
        model = Promotion
        fields = (
            "id",
            "discount_percentage",
            "units_available",
            "start_date",
            "end_date",
            "promotion_code",
        )
        read_only_fields = ("id",)


class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model with active promotions"""

    promotions = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()
    monthly_price = serializers.SerializerMethodField()
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    label_display = serializers.CharField(source="get_label_display", read_only=True)

    class Meta:
        model = Package
        fields = (
            "id",
            "name",
            "currency",
            "amount",
            "monthly_price",
            "description",
            "frequency",
            "frequency_display",
            "label",
            "label_display",
            "extra_info",
            "promotions",
            "discounted_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_promotions(self, obj) -> list:
        """Get active promotions for this package"""
        from datetime import date

        active_promotions = Promotion.objects.filter(
            package=obj,
            start_date__lte=date.today(),
            end_date__gte=date.today(),
        )
        # Filter out promotions with no units available
        active_promotions = [
            promo
            for promo in active_promotions
            if promo.units_available is None or promo.units_available > 0
        ]
        return PromotionSerializer(active_promotions, many=True).data

    def get_discounted_price(self, obj) -> Decimal:
        """Calculate discounted price based on active promotions"""
        promotions = self.get_promotions(obj)
        if not promotions:
            return obj.amount

        # Apply the highest discount
        max_discount = max(promo["discount_percentage"] for promo in promotions)
        discounted_amount = obj.amount * (1 - Decimal(str(max_discount)) / 100)
        return discounted_amount.quantize(Decimal("0.01"))

    def get_monthly_price(self, obj) -> Decimal:
        discounted_price = self.get_discounted_price(obj)
        frequency = obj.frequency
        if frequency == Frequency.ONE_TIME:
            return Decimal("0")

        months_in_freq = {
            Frequency.MONTHLY: 1,
            Frequency.QUARTERLY: 3,
            Frequency.YEARLY: 12,
            Frequency.BIENNIAL: 24,
            Frequency.TRIENNIAL: 36,
            Frequency.QUINQUENNIAL: 60,
        }
        price = (discounted_price / months_in_freq[frequency]).quantize(Decimal("0.01"))
        return f"{price:,.2f}"
