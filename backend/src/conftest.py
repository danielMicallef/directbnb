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
