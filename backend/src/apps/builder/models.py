import uuid
from decimal import Decimal

import stripe
from datetime import timedelta, datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.builder.utils import get_domain
from apps.properties.models import BNBUser
from core.models import AbstractTrackedModel


class ThemeChoices(AbstractTrackedModel):
    name = models.CharField(max_length=255, unique=True)
    preview_link = models.URLField(null=True, blank=True)
    icon_name = models.CharField(max_length=55, null=True, blank=True)

    def get_default_preview_link(self):
        return f"{self.name.lower()}_preview.{get_domain(settings.SITE_URL)}"

    def save(self, *args, **kwargs):
        if not self.preview_link:
            self.preview_link = self.get_default_preview_link()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ColorSchemeChoices(AbstractTrackedModel):
    name = models.CharField(max_length=100, unique=True)
    internal_name = models.CharField(max_length=100, null=True, blank=True)
    theme_colors = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class Website(AbstractTrackedModel):
    owner = models.ForeignKey(BNBUser, on_delete=models.DO_NOTHING)
    theme = models.ForeignKey(ThemeChoices, on_delete=models.RESTRICT)
    color_scheme = models.ForeignKey(ColorSchemeChoices, on_delete=models.RESTRICT)
    airbnb_listing_url = models.URLField(null=True, blank=True)
    booking_listing_url = models.URLField(null=True, blank=True)
    domain_name = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.domain_name} by {self.owner}"


class Frequency(models.IntegerChoices):
    ONE_TIME = 1, "One time payment"
    MONTHLY = 2, "Monthly"
    QUARTERLY = 3, "Quarterly"
    YEARLY = 4, "Yearly"
    BIENNIAL = 5, "Every 2 years"
    TRIENNIAL = 6, "Every 3 years"
    QUINQUENNIAL = 7, "Every 5 years"


class Package(AbstractTrackedModel):
    class LabelChoices(models.TextChoices):
        BUILDER = "Builder", "Builder"
        HOSTING = "Hosting", "Hosting"
        ADDON = "Add-on", "Add-on"

    name = models.CharField(max_length=255, unique=True)
    # List of supported currencies: https://docs.stripe.com/currencies#presentment-currencies
    currency = models.CharField(max_length=10, default="EUR")
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    description = models.CharField(max_length=255, null=True, blank=True)
    frequency = models.PositiveSmallIntegerField(
        choices=Frequency.choices, default=Frequency.ONE_TIME
    )
    label = models.CharField(
        max_length=30, choices=LabelChoices.choices, default=LabelChoices.BUILDER
    )
    extra_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name}, {self.frequency} payments"

    def get_frequency_days(self):
        if self.frequency == self.Frequency.ONE_TIME:
            return None
        if self.frequency == self.Frequency.MONTHLY:
            return 30
        if self.frequency == self.Frequency.QUARTERLY:
            return 90

        for i, label in enumerate(
            [
                self.Frequency.YEARLY,
                self.Frequency.BIENNIAL,
                self.Frequency.TRIENNIAL,
                "Every 4 years",
                self.Frequency.QUINQUENNIAL,
            ]
        ):
            if label != self.frequency:
                return i * 365


class Promotion(AbstractTrackedModel):
    package = models.ForeignKey(Package, on_delete=models.RESTRICT)
    discount_percentage = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )
    units_available = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    promotion_code = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.discount_percentage}% discount for {self.package.name}"


class WebsitePlan(AbstractTrackedModel):
    website = models.ForeignKey(Website, on_delete=models.DO_NOTHING)
    package = models.ForeignKey(Package, on_delete=models.RESTRICT)
    promotion_applied = models.ForeignKey(Promotion, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = ("website", "package")
        verbose_name = "Website Plan Package"
        verbose_name_plural = "Website Plan Packages"

    def __str__(self):
        return f"{self.website} - {self.package}"

    def num_days_for_renewal(self):
        renew_every = self.package.get_frequency_days()
        renew_on = self.created_at + timedelta(days=renew_every)
        days_remaining = (renew_on - datetime.today()).days
        return days_remaining


class LeadRegistration(AbstractTrackedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
    )
    first_name = models.CharField(
        verbose_name="First Name",
        max_length=255,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name="Last Name",
        max_length=255,
        blank=True,
        null=True,
    )
    phone_number = PhoneNumberField(verbose_name="Phone Number", blank=True, null=True)
    theme = models.ForeignKey(
        "builder.ThemeChoices",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    color_scheme = models.ForeignKey(
        "builder.ColorSchemeChoices",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    listing_urls = models.JSONField(default=list, blank=True)
    domain_name = models.CharField(max_length=200, null=True, blank=True)
    extra_requirements = models.JSONField(default=dict, blank=True)
    user = models.ForeignKey(
        BNBUser, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Lead Registration"
        verbose_name_plural = "Lead Registrations"

    def __str__(self):
        return f"{self.email} - {self.first_name or 'N/A'} {self.last_name or 'N/A'}"

    def get_latest_registration_options(self):
        return self.registration_options.order_by(
            "package", "-created_at"
        ).distinct("package")

    def create_checkout_session(self):
        # Create a Stripe Checkout Session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        line_items = []

        # Get the latest registration option for each package
        latest_options = self.get_latest_registration_options()

        for option in latest_options:
            amount = option.package.amount
            name = option.package.name
            if option.promotion:
                amount *= (100 - Decimal(option.promotion.discount_percentage)) / 100
                name = f"{option.package.name} ({option.promotion.discount_percentage}% discount)"

            line_items.append(
                {
                    "price_data": {
                        "currency": option.package.currency,
                        "product_data": {
                            "name": name,
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }
            )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            client_reference_id=self.id,
            success_url=settings.SITE_URL + "/success/",
            cancel_url=settings.SITE_URL + "/cancel/",
        )
        return checkout_session


class RegistrationOptions(AbstractTrackedModel):
    lead_registration = models.ForeignKey(
        LeadRegistration,
        on_delete=models.CASCADE,
        related_name="registration_options",
    )
    promotion = models.ForeignKey(
        "builder.Promotion",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    package = models.ForeignKey(
        "builder.Package",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Registration Option"
        verbose_name_plural = "Registration Options"

    def __str__(self):
        return f"Options for {self.lead_registration.email}"


class StripeWebhookPayload(AbstractTrackedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payload = models.JSONField(default=dict, blank=True)
    lead_registration = models.ForeignKey(
        LeadRegistration,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    processed_successfully = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Stripe Webhook Payload"
        ordering = ["updated_at"]
