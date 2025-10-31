from rest_framework import serializers
from apps.builder.models import ThemeChoices, ColorSchemeChoices, Website


class ThemeChoicesSerializer(serializers.ModelSerializer):
    """Serializer for theme choices"""

    class Meta:
        model = ThemeChoices
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ColorSchemeChoicesSerializer(serializers.ModelSerializer):
    """Serializer for color scheme choices"""

    class Meta:
        model = ColorSchemeChoices
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


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
