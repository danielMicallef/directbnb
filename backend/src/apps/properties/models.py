from django.db import models
from django.contrib.auth import get_user_model

from core.models import AbstractTrackedModel
from apps.builder.models import LeadRegistration

BNBUser = get_user_model()


class PlatformChoices(models.TextChoices):
    AIRBNB = "airbnb", "Airbnb"
    BOOKING = "booking", "Booking.com"
    EXPEDIA = "expedia", "Expedia"
    TRIPADVISOR = "tripadvisor", "Tripadvisor"


class Listing(AbstractTrackedModel):
    title = models.CharField(max_length=255)
    url = models.URLField()
    platform = models.CharField(
        max_length=255,
        choices=PlatformChoices.choices,
        default=PlatformChoices.AIRBNB
    )
    property = models.ForeignKey(
        "properties.Property", on_delete=models.RESTRICT, null=True, blank=True, related_name="listings"
    )
    website = models.ForeignKey(
        "builder.Website", on_delete=models.RESTRICT, null=True, blank=True, related_name="listings"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Listings"


class Property(AbstractTrackedModel):
    owner = models.ForeignKey(BNBUser, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(LeadRegistration, on_delete=models.CASCADE, null=True, blank=True)
    room_type = models.CharField(max_length=255, null=True, blank=True)
    is_super_host = models.BooleanField(default=False)
    home_tier = models.IntegerField(null=True, blank=True)
    person_capacity = models.IntegerField(null=True, blank=True)
    is_guest_favorite = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name_plural = "properties"

    def __str__(self):
        return self.title


class Coordinates(AbstractTrackedModel):
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="coordinates"
    )
    latitude = models.FloatField()
    longitude = models.FloatField()


class Rating(AbstractTrackedModel):
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="rating"
    )
    accuracy = models.FloatField(null=True, blank=True)
    checking = models.FloatField(null=True, blank=True)
    cleanliness = models.FloatField(null=True, blank=True)
    communication = models.FloatField(null=True, blank=True)
    location = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    guest_satisfaction = models.FloatField(null=True, blank=True)
    review_count = models.CharField(max_length=255, null=True, blank=True)


class HouseRules(AbstractTrackedModel):
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="house_rules"
    )
    additional = models.TextField(null=True, blank=True)


class GeneralRule(AbstractTrackedModel):
    house_rules = models.ForeignKey(
        HouseRules, on_delete=models.CASCADE, related_name="general"
    )
    title = models.CharField(max_length=255)


class GeneralRuleValue(AbstractTrackedModel):
    general_rule = models.ForeignKey(
        GeneralRule, on_delete=models.CASCADE, related_name="values"
    )
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)


class Host(AbstractTrackedModel):
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="host"
    )
    host_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)


class SubDescription(AbstractTrackedModel):
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="sub_description"
    )
    title = models.CharField(max_length=255)
    items = models.JSONField(default=list)


class Amenity(AbstractTrackedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="amenities"
    )
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Amenities"


class AmenityValue(AbstractTrackedModel):
    amenity = models.ForeignKey(
        Amenity, on_delete=models.CASCADE, related_name="values"
    )
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=255)
    available = models.BooleanField(default=True)


class Image(AbstractTrackedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="images"
    )
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)  # Keep for reference
    image = models.ImageField(upload_to="property_images/", blank=True, null=True)


class LocationDescription(AbstractTrackedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="location_descriptions"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()


class Highlight(AbstractTrackedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="highlights"
    )
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)


class CoHost(AbstractTrackedModel):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="co_hosts"
    )
    host_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)


class TouristAttraction(AbstractTrackedModel):
    """
    Tourist attractions and points of interest near the property.
    Used for the "Discover {Location}" section on the website.
    """
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="attractions"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    distance = models.CharField(max_length=100, help_text="e.g., '2 km away', '10 min walk'")
    category = models.CharField(
        max_length=100,
        help_text="e.g., 'Restaurant', 'Museum', 'Beach', 'Park'"
    )
    image = models.ImageField(upload_to="attractions/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Fallback if image not uploaded")
    google_maps_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order, lower numbers first")

    class Meta:
        ordering = ['order', 'distance']
        verbose_name = "Tourist Attraction"
        verbose_name_plural = "Tourist Attractions"

    def __str__(self):
        return f"{self.name} - {self.property.title}"


class Article(AbstractTrackedModel):
    """
    Blog articles/guides created by property hosts.
    Used for content marketing and SEO.
    """
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="articles"
    )
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=255)
    content = models.TextField(help_text="Article content in Markdown or HTML")
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags, e.g., ['beach', 'family', 'adventure']"
    )
    read_time = models.IntegerField(
        default=5,
        help_text="Estimated read time in minutes"
    )
    featured_image = models.ImageField(upload_to="articles/", blank=True, null=True)
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

