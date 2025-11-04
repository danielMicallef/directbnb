from datetime import timedelta, datetime

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

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


class Package(AbstractTrackedModel):
    class Frequency(models.IntegerChoices):
        ONE_TIME = 1, "One time payment"
        MONTHLY = 2, "Monthly"
        QUARTERLY = 3, "Quarterly"
        YEARLY = 4, "Yearly"
        BIENNIAL = 5, "Every 2 years"
        TRIENNIAL = 6, "Every 3 years"
        QUINQUENNIAL = 7, "Every 5 years"

    class LabelChoices(models.TextChoices):
        BUILDER = "Builder", "Builder"
        HOSTING = "Hosting", "Hosting"
        ADDON = "Add-on", "Add-on"

    name = models.CharField(max_length=255, unique=True)
    amount = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=255, null=True, blank=True)
    frequency = models.PositiveSmallIntegerField(
        choices=Frequency.choices, default=Frequency.ONE_TIME
    )
    label = models.CharField(
        max_length=30, choices=LabelChoices.choices, default=LabelChoices.BUILDER
    )

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
