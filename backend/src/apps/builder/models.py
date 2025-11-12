import uuid
from decimal import Decimal

import stripe
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from apps.builder.utils import get_domain
from core.models import AbstractTrackedModel

BNBUser = get_user_model()


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

    def is_promotion_available(self):
        today = timezone.now().date()
        if not self.units_available and self.units_available < 0:
            return False

        if self.start_date and today < self.start_date:
            return False

        if self.end_date and today > self.end_date:
            return False

        return True

    def get_discounted_amount(self, check_available=True):
        """
        :param check_available: bool (If True, return default amount if promotion is no longer valid)
        :return: package amount
        """
        amount = self.package.amount
        if not self.is_promotion_available() and check_available:
            return amount
        amount *= (100 - Decimal(self.discount_percentage)) / 100
        return amount

    def get_promotional_name(self, check_available=True):
        """
        :param check_available: bool (If True, return default name if promotion is no longer valid)
        :return: package name
        """
        name = self.package.name
        if not self.is_promotion_available() and check_available:
            return name

        return f"{name} ({self.discount_percentage}% discount)"

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

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_latest_registration_options(self):
        return self.registration_options.order_by("package", "-created_at").distinct(
            "package"
        )

    def create_user_from_lead(self):
        user, created = BNBUser.objects.get_or_create(
            email=self.email,
            defaults={
                "first_name": self.first_name,
                "last_name": self.last_name,
                "phone_number": self.phone_number,
                "is_active": True,
                "is_email_confirmed": False,
            },
        )
        if created:
            user.set_unusable_password()
            self.user = user
            self.save(update_fields=["user"])
            user.save(update_fields=["password"])

        return user, created

    def send_payment_confirmation_email(self):
        """
        Send payment confirmation email with email verification link.
        """

        # Get or create user
        if not self.user:
            user, created = self.create_user_from_lead()

        token = self.user.refresh_user_token()

        # Build verification URL
        verification_url = reverse("users:verify_email", kwargs={"token": token})
        full_verification_url = f"{settings.SITE_URL}{verification_url}"

        # Get registration options with calculated discounted amounts
        registration_options = []
        total_amount = Decimal("0.00")
        total_currency = "EUR"  # Default currency

        for option in self.get_latest_registration_options():
            amount = option.package.amount
            if option.promotion:
                amount = option.promotion.get_discounted_amount(check_available=False)

            registration_options.append(
                {
                    "package": option.package,
                    "promotion": option.promotion,
                    "discounted_amount": amount,
                }
            )

            total_amount += amount
            total_currency = option.package.currency

        # Render email template
        context = {
            "user": self.user,
            "verification_url": full_verification_url,
            "registration_options": registration_options,
            "total_amount": total_amount,
            "total_currency": total_currency,
            "site_name": settings.SITE_NAME,
        }

        html_message = render_to_string(
            "builder/emails/payment_confirmation.html", context
        )

        # Send email
        self.user.email_user(
            subject=f"Payment Confirmed - Welcome to {settings.SITE_NAME}!",
            message="",  # Plain text version (optional)
            html_message=html_message,
        )

    def create_checkout_session(self):
        # Create a Stripe Checkout Session
        stripe.api_key = settings.STRIPE_SECRET_KEY
        line_items = []

        # Get the latest registration option for each package
        latest_options = self.get_latest_registration_options()

        for option in latest_options:
            amount = option.package.amount
            name = option.package.name
            if promotion := option.promotion:
                amount = promotion.get_discounted_amount()
                name = promotion.get_promotional_name()

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
