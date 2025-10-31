from django.db import models

from core.models import AbstractTrackedModel


class ThemeChoices(AbstractTrackedModel):
    name = models.CharField(max_length=255, unique=True)


class ColorSchemeChoices(AbstractTrackedModel):
    name = models.CharField(max_length=255, unique=True)


class Website(AbstractTrackedModel):
    theme = models.ForeignKey(ThemeChoices, on_delete=models.RESTRICT)
    color_scheme = models.ForeignKey(ColorSchemeChoices, on_delete=models.RESTRICT)
    airbnb_listing_url = models.URLField(null=True, blank=True)
    booking_listing_url = models.URLField(null=True, blank=True)
    domain_name = models.URLField(null=True, blank=True)
