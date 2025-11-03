from django.db import models
from django.contrib.auth import get_user_model

from core.models import AbstractTrackedModel

BNBUser = get_user_model()


class Property(AbstractTrackedModel):
    owner = models.ForeignKey(BNBUser, on_delete=models.CASCADE)
    room_type = models.CharField(max_length=255, null=True, blank=True)
    is_super_host = models.BooleanField(default=False)
    home_tier = models.IntegerField(null=True, blank=True)
    person_capacity = models.IntegerField(null=True, blank=True)
    is_guest_favorite = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=10, null=True, blank=True)

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
    url = models.URLField()


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
