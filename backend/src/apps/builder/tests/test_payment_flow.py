import json
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core import mail
from django.urls import reverse

from apps.builder.models import LeadRegistration, RegistrationOptions
from apps.builder.tests.test_utils import generate_stripe_signature
from apps.users.models import BNBUser, UserToken


# Stripe webhook secret for testing
STRIPE_WEBHOOK_SECRET = "whsec_e136fcf022bbf4fe4d31d2ca7f62c3b9d3bb824beb1368d6c592eb38b137cc06"

@pytest.fixture()
def lead_data():
    return {
        "email": "testuser@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+35677777777",
        "domain_name": "johndoe-property.com",
        "listing_urls": ["https://airbnb.com/rooms/12345"],
    }


@pytest.mark.django_db
class TestCompletePaymentFlow:
    """
    Integration test for the complete payment flow:
    1. Create LeadRegistration via API
    2. Create RegistrationOptions via API
    3. Simulate Stripe webhook
    4. Verify user creation
    5. Verify email sent with verification link
    """
    def get_webhook_payload(self, lead_registration_id):
        webhook_payload = {
            "id": "evt_test_payment_flow",
            "object": "event",
            "api_version": "2023-10-16",
            "created": 1234567890,
            "data": {
                "object": {
                    "id": "cs_test_payment_flow",
                    "object": "checkout.session",
                    "amount_total": 50000,  # $500.00
                    "currency": "eur",
                    "customer": "cus_test123",
                    "payment_status": "paid",
                    "client_reference_id": str(lead_registration_id),
                    "metadata": {},
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {"id": None, "idempotency_key": None},
            "type": "checkout.session.completed",
        }
        return webhook_payload

    def test_complete_payment_flow_with_user_creation_and_email(
        self, api_client, all_packages, promotion_factory, lead_data
    ):
        """
        Test the complete flow from lead registration to user creation and email verification
        """
        # Step 1: Create a promotion for the builder package
        builder_package = all_packages["builder"]
        today = date.today()

        promotion = promotion_factory(
            package=builder_package,
            discount_percentage=50,
            units_available=100,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            promotion_code="WELCOME50",
        )

        # Step 2: Create LeadRegistration via API
        lead_url = reverse("builder_api:lead-registration-list")


        lead_response = api_client.post(
            lead_url, data=lead_data, format="json"
        )
        assert lead_response.status_code == 201
        lead_registration_id = lead_response.data["id"]

        # Verify lead was created
        lead_registration = LeadRegistration.objects.get(id=lead_registration_id)
        assert lead_registration.email == lead_data.get("email")
        assert lead_registration.first_name == lead_data.get("first_name")
        assert lead_registration.last_name == lead_data.get("last_name")

        # Step 3: Create 2 RegistrationOptions via API
        options_url = reverse("builder_api:registration-options-list")

        # First option: Builder package with promotion
        option1_data = {
            "lead_registration": lead_registration_id,
            "package": builder_package.id,
            "promotion": promotion.id,
        }
        option1_response = api_client.post(
            options_url, data=option1_data, format="json"
        )
        assert option1_response.status_code == 201
        option1_id = option1_response.data["id"]

        # Second option: Hosting package (no promotion)
        hosting_package = all_packages["hosting_1_year"]
        option2_data = {
            "lead_registration": lead_registration_id,
            "package": hosting_package.id,
        }
        option2_response = api_client.post(
            options_url, data=option2_data, format="json"
        )
        assert option2_response.status_code == 201
        option2_id = option2_response.data["id"]

        # Verify registration options were created
        option1 = RegistrationOptions.objects.get(id=option1_id)
        option2 = RegistrationOptions.objects.get(id=option2_id)
        assert option1.paid_at is None
        assert option2.paid_at is None

        # Step 4: Simulate Stripe webhook for checkout.session.completed
        webhook_url = reverse("builder_api:stripe-webhook")
        webhook_payload = self.get_webhook_payload(lead_registration_id)

        payload_bytes = json.dumps(webhook_payload).encode("utf-8")
        signature = generate_stripe_signature(payload_bytes, STRIPE_WEBHOOK_SECRET)

        user = BNBUser.objects.filter(email=lead_data.get("email")).first()
        assert user is None
        # Clear any existing emails
        mail.outbox = []
        webhook_response = api_client.post(
            webhook_url,
            data=payload_bytes,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )
        assert webhook_response.status_code == 200

        # Step 5: Verify all registration options have paid_at timestamp
        option1.refresh_from_db()
        option2.refresh_from_db()

        assert option1.paid_at is not None, "Option 1 should have paid_at timestamp"
        assert option2.paid_at is not None, "Option 2 should have paid_at timestamp"

        # Step 6: Verify user was created from LeadRegistration
        user = BNBUser.objects.filter(email=lead_data.get("email")).first()
        assert user is not None, "User should be created from lead registration"
        assert user.first_name == lead_data.get("first_name")
        assert user.last_name == lead_data.get("last_name")
        assert str(user.phone_number) == lead_data.get("phone_number")
        assert user.is_active is True
        assert user.is_email_confirmed is False, "Email should not be confirmed yet"
        assert not user.has_usable_password(), "User should not have a usable password"

        # Verify lead registration is linked to user
        lead_registration.refresh_from_db()
        assert lead_registration.user == user

        # Step 7: Verify verification token was created
        user_token = UserToken.objects.filter(user=user).first()
        assert user_token is not None, "Verification token should be created"
        assert user_token.is_expired is False, "Token should not be expired"

        # Step 8: Verify email was sent
        assert len(mail.outbox) == 1, "One email should be sent"
        email = mail.outbox[0]

        # Verify email details
        assert email.to == ["testuser@example.com"]
        assert "Payment Confirmed" in email.subject
        assert "Welcome" in email.subject

        # Verify email content contains required information
        email_body = email.alternatives[0].content
        assert lead_data.get("first_name") in email_body, "Email should contain user's first name"
        assert "verify" in email_body, "Email should mention email verification"

        # Step 9: Verify verification URL is in the email
        verification_url_part = f"/users/verify-email/{user_token.token}"
        assert (
            verification_url_part in email_body
            or str(user_token.token) in email_body
        ), "Email should contain verification URL with token"

        # Step 10: Verify payment summary is in the email
        assert (
            builder_package.name in email_body
        ), "Email should contain builder package name"
        assert (
            hosting_package.name in email_body
        ), "Email should contain hosting package name"

        # Verify promotion discount is mentioned
        assert "50%" in email_body or "discount" in email_body.lower()

    def test_payment_flow_with_existing_user(
        self, api_client, all_packages, user_factory
    ):
        """
        Test payment flow when user with email already exists
        """
        # Step 1: Create an existing user
        existing_user = user_factory(
            email="existing@example.com",
            first_name="Jane",
            last_name="Smith",
            is_email_confirmed=True,
        )
        existing_user.save()

        # Step 2: Create LeadRegistration with same email
        lead_url = reverse("builder_api:lead-registration-list")
        lead_data = {
            "email": "existing@example.com",
            "first_name": "Jane",
            "last_name": "Smith Updated",  # Different last name
            "phone_number": "+35677777777",
            "listing_urls": []
        }

        lead_response = api_client.post(lead_url, data=lead_data, format="json")
        assert lead_response.status_code == 400
        assert "A user with this email already exists." in lead_response.json().get("email")[0]


    def test_payment_flow_multiple_packages_with_promotions(
        self, api_client, all_packages, promotion_factory, lead_data
    ):
        """
        Test payment flow with multiple packages and different promotions
        """
        today = date.today()

        # Create promotions for different packages
        builder_package = all_packages["builder"]
        hosting_package = all_packages["hosting_3_years"]
        addon_package = all_packages["addon_instantly_update"]

        builder_promotion = promotion_factory(
            package=builder_package,
            discount_percentage=50,
            units_available=50,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            promotion_code="BUILDER50",
        )

        hosting_promotion = promotion_factory(
            package=hosting_package,
            discount_percentage=30,
            units_available=100,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=60),
            promotion_code="HOST30",
        )

        # Create lead registration
        lead_url = reverse("builder_api:lead-registration-list")
        lead_data.update({
            "email": "multipackage@example.com",
            "first_name": "Multi",
            "last_name": "Package",
        })
        lead_response = api_client.post(lead_url, data=lead_data, format="json")
        assert lead_response.status_code == 201
        lead_registration_id = lead_response.data["id"]

        # Create multiple registration options
        options_url = reverse("builder_api:registration-options-list")

        # Builder with promotion
        api_client.post(
            options_url,
            data={
                "lead_registration": lead_registration_id,
                "package": builder_package.id,
                "promotion": builder_promotion.id,
            },
            format="json",
        )

        # Hosting with promotion
        api_client.post(
            options_url,
            data={
                "lead_registration": lead_registration_id,
                "package": hosting_package.id,
                "promotion": hosting_promotion.id,
            },
            format="json",
        )

        # Add-on without promotion
        api_client.post(
            options_url,
            data={
                "lead_registration": lead_registration_id,
                "package": addon_package.id,
            },
            format="json",
        )

        # Simulate webhook
        webhook_url = reverse("builder_api:stripe-webhook")
        webhook_payload = {
            "id": "evt_test_multi",
            "object": "event",
            "api_version": "2023-10-16",
            "created": 1234567890,
            "data": {
                "object": {
                    "id": "cs_test_multi",
                    "object": "checkout.session",
                    "amount_total": 100000,
                    "currency": "eur",
                    "payment_status": "paid",
                    "client_reference_id": str(lead_registration_id),
                }
            },
            "livemode": False,
            "type": "checkout.session.completed",
        }

        payload_bytes = json.dumps(webhook_payload).encode("utf-8")
        signature = generate_stripe_signature(payload_bytes, STRIPE_WEBHOOK_SECRET)

        mail.outbox = []

        webhook_response = api_client.post(
            webhook_url,
            data=payload_bytes,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

        assert webhook_response.status_code == 200

        # Verify all 3 registration options have paid_at
        lead_registration = LeadRegistration.objects.get(id=lead_registration_id)
        paid_options = lead_registration.registration_options.filter(
            paid_at__isnull=False
        )
        assert paid_options.count() == 3, "All 3 options should be marked as paid"

        # Verify user created
        user = BNBUser.objects.get(email="multipackage@example.com")
        assert user is not None

        # Verify email sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        email_body = email.alternatives[0].content

        # Verify all packages mentioned in email
        assert builder_package.name in email_body
        assert hosting_package.name in email_body
        assert addon_package.name in email_body

        # Verify promotions mentioned
        assert "50%" in email_body or "30%" in email_body

    def test_payment_flow_calculates_correct_totals_in_email(
        self, api_client, all_packages, promotion_factory
    ):
        """
        Test that email contains correct total amounts with discounts
        """
        today = date.today()
        builder_package = all_packages["builder"]

        # Create 50% off promotion
        promotion = promotion_factory(
            package=builder_package,
            discount_percentage=50,
            units_available=100,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
        )

        # Create lead and option
        lead_url = reverse("builder_api:lead-registration-list")
        lead_response = api_client.post(
            lead_url,
            data={"email": "total@example.com", "first_name": "Total", "last_name": "Test", "listing_urls": []},
            format="json",
        )
        lead_registration_id = lead_response.data["id"]

        options_url = reverse("builder_api:registration-options-list")
        api_client.post(
            options_url,
            data={
                "lead_registration": lead_registration_id,
                "package": builder_package.id,
                "promotion": promotion.id,
            },
            format="json",
        )

        # Simulate webhook
        webhook_url = reverse("builder_api:stripe-webhook")
        webhook_payload = {
            "id": "evt_test_totals",
            "object": "event",
            "api_version": "2023-10-16",
            "created": 1234567890,
            "data": {
                "object": {
                    "id": "cs_test_totals",
                    "object": "checkout.session",
                    "payment_status": "paid",
                    "client_reference_id": str(lead_registration_id),
                }
            },
            "livemode": False,
            "type": "checkout.session.completed",
        }

        payload_bytes = json.dumps(webhook_payload).encode("utf-8")
        signature = generate_stripe_signature(payload_bytes, STRIPE_WEBHOOK_SECRET)

        mail.outbox = []

        api_client.post(
            webhook_url,
            data=payload_bytes,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

        # Verify email contains correct amounts
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        email_body = email.alternatives[0].content

        # Calculate expected discounted price
        original_price = builder_package.amount
        discounted_price = original_price * Decimal("0.5")  # 50% off

        # Verify original and discounted prices are in email
        # Note: Exact formatting may vary, so we check for the presence of key numbers
        assert str(original_price) in email_body or str(int(original_price)) in email_body
        assert str(discounted_price) in email_body or str(int(discounted_price)) in email_body
