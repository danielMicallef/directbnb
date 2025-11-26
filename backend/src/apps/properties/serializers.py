from rest_framework import serializers

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
    TouristAttraction,
    Article,
)


class GeneralRuleValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralRuleValue
        fields = ["id", "title", "icon", "created_at", "updated_at"]


class GeneralRuleSerializer(serializers.ModelSerializer):
    values = GeneralRuleValueSerializer(many=True, read_only=True)

    class Meta:
        model = GeneralRule
        fields = ["id", "title", "values", "created_at", "updated_at"]


class HouseRulesSerializer(serializers.ModelSerializer):
    general = GeneralRuleSerializer(many=True, read_only=True)

    class Meta:
        model = HouseRules
        fields = ["id", "additional", "general", "created_at", "updated_at"]


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ["id", "latitude", "longitude", "created_at", "updated_at"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            "id",
            "accuracy",
            "checking",
            "cleanliness",
            "communication",
            "location",
            "value",
            "guest_satisfaction",
            "review_count",
            "created_at",
            "updated_at",
        ]


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ["id", "host_id", "name", "created_at", "updated_at"]


class SubDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDescription
        fields = ["id", "title", "items", "created_at", "updated_at"]


class AmenityValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityValue
        fields = [
            "id",
            "title",
            "subtitle",
            "icon",
            "available",
            "created_at",
            "updated_at",
        ]


class AmenitySerializer(serializers.ModelSerializer):
    values = AmenityValueSerializer(many=True, read_only=True)

    class Meta:
        model = Amenity
        fields = ["id", "title", "values", "created_at", "updated_at"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "title", "url", "created_at", "updated_at"]


class LocationDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationDescription
        fields = ["id", "title", "content", "created_at", "updated_at"]


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ["id", "title", "subtitle", "icon", "created_at", "updated_at"]


class CoHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoHost
        fields = ["id", "host_id", "name", "created_at", "updated_at"]


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for property list view"""

    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "owner_email",
            "title",
            "room_type",
            "person_capacity",
            "is_guest_favorite",
            "is_super_host",
            "created_at",
            "updated_at",
        ]


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Complete serializer with all related data"""

    coordinates = CoordinatesSerializer(read_only=True)
    rating = RatingSerializer(read_only=True)
    house_rules = HouseRulesSerializer(read_only=True)
    host = HostSerializer(read_only=True)
    sub_description = SubDescriptionSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    location_descriptions = LocationDescriptionSerializer(many=True, read_only=True)
    highlights = HighlightSerializer(many=True, read_only=True)
    co_hosts = CoHostSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "owner_email",
            "room_type",
            "is_super_host",
            "home_tier",
            "person_capacity",
            "is_guest_favorite",
            "description",
            "title",
            "language",
            "coordinates",
            "rating",
            "house_rules",
            "host",
            "sub_description",
            "amenities",
            "images",
            "location_descriptions",
            "highlights",
            "co_hosts",
            "created_at",
            "updated_at",
        ]


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating properties with nested data"""

    coordinates = CoordinatesSerializer(required=False)
    rating = RatingSerializer(required=False)
    house_rules = HouseRulesSerializer(required=False)
    host = HostSerializer(required=False)
    sub_description = SubDescriptionSerializer(required=False)
    amenities = AmenitySerializer(many=True, required=False)
    images = ImageSerializer(many=True, required=False)
    location_descriptions = LocationDescriptionSerializer(many=True, required=False)
    highlights = HighlightSerializer(many=True, required=False)
    co_hosts = CoHostSerializer(many=True, required=False)

    class Meta:
        model = Property
        fields = [
            "id",
            "room_type",
            "is_super_host",
            "home_tier",
            "person_capacity",
            "is_guest_favorite",
            "description",
            "title",
            "language",
            "coordinates",
            "rating",
            "house_rules",
            "host",
            "sub_description",
            "amenities",
            "images",
            "location_descriptions",
            "highlights",
            "co_hosts",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        # Handle nested updates for related models
        coordinates_data = validated_data.pop("coordinates", None)
        rating_data = validated_data.pop("rating", None)
        house_rules_data = validated_data.pop("house_rules", None)
        host_data = validated_data.pop("host", None)
        sub_description_data = validated_data.pop("sub_description", None)
        amenities_data = validated_data.pop("amenities", None)
        images_data = validated_data.pop("images", None)
        location_descriptions_data = validated_data.pop("location_descriptions", None)
        highlights_data = validated_data.pop("highlights", None)
        co_hosts_data = validated_data.pop("co_hosts", None)

        # Update main property fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create coordinates
        if coordinates_data:
            Coordinates.objects.update_or_create(
                property=instance, defaults=coordinates_data
            )

        # Update or create rating
        if rating_data:
            Rating.objects.update_or_create(property=instance, defaults=rating_data)

        # Update or create host
        if host_data:
            Host.objects.update_or_create(property=instance, defaults=host_data)

        # Update or create sub_description
        if sub_description_data:
            SubDescription.objects.update_or_create(
                property=instance, defaults=sub_description_data
            )

        # Update house rules (complex nested structure)
        if house_rules_data:
            house_rules_obj, _ = HouseRules.objects.update_or_create(
                property=instance,
                defaults={"additional": house_rules_data.get("additional")},
            )

        # Update many-to-many style relationships
        if amenities_data is not None:
            instance.amenities.all().delete()
            for amenity_data in amenities_data:
                Amenity.objects.create(property=instance, **amenity_data)

        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                Image.objects.create(property=instance, **image_data)

        if location_descriptions_data is not None:
            instance.location_descriptions.all().delete()
            for loc_desc_data in location_descriptions_data:
                LocationDescription.objects.create(property=instance, **loc_desc_data)

        if highlights_data is not None:
            instance.highlights.all().delete()
            for highlight_data in highlights_data:
                Highlight.objects.create(property=instance, **highlight_data)

        if co_hosts_data is not None:
            instance.co_hosts.all().delete()
            for co_host_data in co_hosts_data:
                CoHost.objects.create(property=instance, **co_host_data)

        return instance


class TouristAttractionSerializer(serializers.ModelSerializer):
    """Serializer for tourist attractions near the property"""

    class Meta:
        model = TouristAttraction
        fields = [
            "id",
            "name",
            "description",
            "distance",
            "category",
            "image",
            "image_url",
            "google_maps_url",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for property articles/blogs"""

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "subtitle",
            "slug",
            "content",
            "tags",
            "read_time",
            "featured_image",
            "published",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at", "published_at"]
