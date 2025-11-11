import os

import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure test database settings"""
    from django.conf import settings as django_settings

    # Ensure all required database keys are present
    db_config = django_settings.DATABASES["default"]

    # Add missing keys with defaults
    db_config.setdefault("ATOMIC_REQUESTS", False)
    db_config.setdefault("AUTOCOMMIT", True)
    db_config.setdefault("CONN_MAX_AGE", 0)
    db_config.setdefault("OPTIONS", {})
    db_config.setdefault("TIME_ZONE", None)

    # Set test database name
    if "TEST" not in db_config:
        db_config["TEST"] = {}
    db_config["TEST"]["NAME"] = "test_directbnb"


@pytest.fixture
def api_client():
    """Return an API client for testing"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(db, api_client):
    """Return an authenticated API client"""
    from apps.users.models import BNBUser

    user = BNBUser.objects.create_user(
        email="test@example.com", password="testpass123", phone_number="+1234567890"
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture(scope="session", autouse=True)
def setup_test_settings():
    """Configure test-specific settings"""
    # Set Stripe webhook secret for testing
    os.environ["STRIPE_WEBHOOK_SECRET"] = (
        "whsec_e136fcf022bbf4fe4d31d2ca7f62c3b9d3bb824beb1368d6c592eb38b137cc06"
    )

    # Reload settings to pick up the new environment variable
    if hasattr(settings, "STRIPE_WEBHOOK_SECRET"):
        settings.STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

    # Disable DRF throttling for tests to avoid 429 errors
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}


# Factory fixtures registration
from pytest_factoryboy import register
from apps.builder.tests import factories as builder_factories
from apps.users.tests import factories as user_factories


# Builder app factories
register(builder_factories.ThemeChoicesFactory)
register(builder_factories.ColorSchemeChoicesFactory)
register(builder_factories.WebsiteFactory)
register(builder_factories.PackageFactory)
register(builder_factories.PromotionFactory)
register(builder_factories.WebsitePlanFactory)
register(builder_factories.LeadRegistrationFactory)
register(builder_factories.RegistrationOptionsFactory)
register(builder_factories.StripeWebhookPayloadFactory)

# Users app factories
register(user_factories.UserFactory)
register(user_factories.UserTokenFactory)


@pytest.fixture
def all_packages():
    """Creates all predefined package instances."""
    from apps.builder.models import Package, Frequency
    from decimal import Decimal

    return {
        "addon_instantly_update": builder_factories.PackageFactory(
            label=Package.LabelChoices.ADDON,
            name="Test:Instantly update live reviews",
            amount=Decimal("60.00"),
            frequency=Frequency.YEARLY,
            description="Earn trust by showcasing live reviews from Airbnb, Booking.com, Expedia",
        ),
        "hosting_3_years": builder_factories.PackageFactory(
            label=Package.LabelChoices.HOSTING,
            name="Test:We host for 3 years",
            amount=Decimal("594.00"),
            frequency=Frequency.TRIENNIAL,
            description="Commit for 3 years to enjoy heavy discounts",
        ),
        "hosting_1_year": builder_factories.PackageFactory(
            label=Package.LabelChoices.HOSTING,
            name="Test:We host for 1 year",
            amount=Decimal("299.00"),
            frequency=Frequency.YEARLY,
            description="We take care of securely hosting your website.",
        ),
        "hosting_self": builder_factories.PackageFactory(
            label=Package.LabelChoices.HOSTING,
            name="Test:Host the site yourself",
            amount=Decimal("0.00"),
            frequency=Frequency.ONE_TIME,
            description="We'll provide instructions on how to host yourself.",
        ),
        "builder_custom": builder_factories.PackageFactory(
            label=Package.LabelChoices.BUILDER,
            name="Test:Custom Package",
            amount=Decimal("3500.00"),
            frequency=Frequency.ONE_TIME,
            description="Work with our developers to create your fully custom website.",
        ),
        "builder": builder_factories.PackageFactory(
            label=Package.LabelChoices.BUILDER,
            name="Test:Builder Package",
            amount=Decimal("650.00"),
            frequency=Frequency.ONE_TIME,
            description="Launch your branded direct booking site",
        ),
    }
