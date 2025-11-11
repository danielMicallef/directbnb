"""Factories for the builder app."""

import factory
from factory.faker import Faker

from apps.builder import models
from apps.users.tests.factories import UserFactory


class ThemeChoicesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ThemeChoices

    name = Faker("word")
    preview_link = Faker("url")
    icon_name = Faker("word")


class ColorSchemeChoicesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ColorSchemeChoices

    name = Faker("color_name")
    internal_name = Faker("color_name")
    theme_colors = factory.LazyFunction(dict)


class WebsiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Website

    owner = factory.SubFactory(UserFactory)
    theme = factory.SubFactory(ThemeChoicesFactory)
    color_scheme = factory.SubFactory(ColorSchemeChoicesFactory)
    airbnb_listing_url = Faker("url")
    booking_listing_url = Faker("url")
    domain_name = Faker("url")


class PackageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Package

    name = factory.Sequence(lambda n: f"Package {n}")
    currency = "EUR"
    amount = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    description = Faker("sentence")
    frequency = factory.Iterator(models.Frequency.values)
    label = factory.Iterator(models.Package.LabelChoices.values)
    extra_info = factory.LazyFunction(dict)


class PromotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Promotion

    package = factory.SubFactory(PackageFactory)
    discount_percentage = Faker("random_int", min=1, max=100)
    units_available = Faker("random_int", min=1, max=100)
    start_date = Faker("past_date")
    end_date = Faker("future_date")
    promotion_code = Faker("pystr", max_chars=10)


class WebsitePlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WebsitePlan

    website = factory.SubFactory(WebsiteFactory)
    package = factory.SubFactory(PackageFactory)
    promotion_applied = factory.SubFactory(PromotionFactory)


class LeadRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LeadRegistration

    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    phone_number = Faker("phone_number")
    theme = factory.SubFactory(ThemeChoicesFactory)
    color_scheme = factory.SubFactory(ColorSchemeChoicesFactory)
    listing_urls = factory.LazyFunction(list)
    domain_name = Faker("domain_name")
    extra_requirements = factory.LazyFunction(dict)
    user = factory.SubFactory(UserFactory)
    completed_at = None


class RegistrationOptionsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RegistrationOptions

    lead_registration = factory.SubFactory(LeadRegistrationFactory)
    promotion = factory.SubFactory(PromotionFactory)
    package = factory.SubFactory(PackageFactory)
    paid_at = None
    expires_at = None


class StripeWebhookPayloadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StripeWebhookPayload

    payload = factory.LazyFunction(dict)
    lead_registration = factory.SubFactory(LeadRegistrationFactory)
    completed_at = None
    processed_successfully = False
