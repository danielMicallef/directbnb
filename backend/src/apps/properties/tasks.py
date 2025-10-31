from pyairbnb import details

from celery import shared_task

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import (
    Property,
    Coordinates,
    Rating,
    HouseRules,
    GeneralRule,
    GeneralRuleValue,
    Host,
    SubDescription,
    Amenity,
    AmenityValue,
    Image,
    LocationDescription,
    Highlight,
    CoHost,
)

BNBUser = get_user_model()


def get_airbnb_data_from_url(room_url: str, proxy_url: str = ""):
    if not proxy_url:
        proxy_url = settings.SCRAPE_PROXY_URL

    data, price_input, cookies = details.get(
        room_url, language="en", proxy_url=proxy_url
    )
    return data


def save_property_data(data: dict, owner_id: int) -> Property:
    """
    Save scraped Airbnb data to the database.

    Args:
        data: Dictionary containing property data from Airbnb scraper
        owner_id: ID of the user who owns this property

    Returns:
        Property instance
    """
    owner = BNBUser.objects.get(id=owner_id)

    # Create main property
    property_obj = Property.objects.create(
        owner=owner,
        room_type=data.get("room_type"),
        is_super_host=data.get("is_super_host", False),
        home_tier=data.get("home_tier"),
        person_capacity=data.get("person_capacity"),
        is_guest_favorite=data.get("is_guest_favorite", False),
        description=data.get("description"),
        title=data.get("title"),
        language=data.get("language"),
    )

    # Create coordinates
    if coords := data.get("coordinates"):
        Coordinates.objects.create(
            property=property_obj,
            latitude=coords.get("latitude"),
            longitude=coords.get("longitude"),
        )

    # Create rating
    if rating := data.get("rating"):
        Rating.objects.create(
            property=property_obj,
            accuracy=rating.get("accuracy"),
            checking=rating.get("checking"),
            cleanliness=rating.get("cleanliness"),
            communication=rating.get("communication"),
            location=rating.get("location"),
            value=rating.get("value"),
            guest_satisfaction=rating.get("guest_satisfaction"),
            review_count=rating.get("review_count"),
        )

    # Create house rules
    if house_rules := data.get("house_rules"):
        house_rules_obj = HouseRules.objects.create(
            property=property_obj,
            additional=house_rules.get("aditional"),
        )

        # Create general rules
        for general_rule in house_rules.get("general", []):
            general_rule_obj = GeneralRule.objects.create(
                house_rules=house_rules_obj,
                title=general_rule.get("title"),
            )

            # Create general rule values
            for value in general_rule.get("values", []):
                GeneralRuleValue.objects.create(
                    general_rule=general_rule_obj,
                    title=value.get("title"),
                    icon=value.get("icon"),
                )

    # Create host
    if host := data.get("host"):
        Host.objects.create(
            property=property_obj,
            host_id=host.get("id"),
            name=host.get("name"),
        )

    # Create sub description
    if sub_desc := data.get("sub_description"):
        SubDescription.objects.create(
            property=property_obj,
            title=sub_desc.get("title"),
            items=sub_desc.get("items", []),
        )

    # Create amenities
    for amenity in data.get("amenities", []):
        amenity_obj = Amenity.objects.create(
            property=property_obj,
            title=amenity.get("title"),
        )

        # Create amenity values
        for value in amenity.get("values", []):
            AmenityValue.objects.create(
                amenity=amenity_obj,
                title=value.get("title"),
                subtitle=value.get("subtitle"),
                icon=value.get("icon"),
                available=value.get("available", True),
            )

    # Create images
    for image in data.get("images", []):
        Image.objects.create(
            property=property_obj,
            title=image.get("title"),
            url=image.get("url"),
        )

    # Create location descriptions
    for loc_desc in data.get("location_descriptions", []):
        LocationDescription.objects.create(
            property=property_obj,
            title=loc_desc.get("title"),
            content=loc_desc.get("content"),
        )

    # Create highlights
    for highlight in data.get("highlights", []):
        Highlight.objects.create(
            property=property_obj,
            title=highlight.get("title"),
            subtitle=highlight.get("subtitle"),
            icon=highlight.get("icon"),
        )

    # Create co-hosts
    for co_host in data.get("co_hosts", []):
        CoHost.objects.create(
            property=property_obj,
            host_id=co_host.get("id"),
            name=co_host.get("name"),
        )

    return property_obj


@shared_task(bind=True, max_retries=3)
def scrape_airbnb_listing(self, listing_url: str, owner_id: int):
    """
    Celery task to scrape an Airbnb listing and save it to the database.

    Args:
        listing_url: URL of the Airbnb listing
        owner_id: ID of the user who owns this property
    """
    try:
        data = get_airbnb_data_from_url(listing_url)
        property_obj = save_property_data(data, owner_id)
        return {"success": True, "property_id": property_obj.id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
