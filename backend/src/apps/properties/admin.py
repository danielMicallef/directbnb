from django.contrib import admin

from apps.properties.models import (
    Amenity,
    AmenityValue,
    CoHost,
    Coordinates,
    GeneralRule,
    GeneralRuleValue,
    Highlight,
    Host,
    HouseRules,
    Image,
    LocationDescription,
    Property,
    Rating,
    SubDescription,
)


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AmenityValueInline(admin.TabularInline):
    model = AmenityValue
    extra = 1


class GeneralRuleValueInline(admin.TabularInline):
    model = GeneralRuleValue
    extra = 1


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class LocationDescriptionInline(admin.TabularInline):
    model = LocationDescription
    extra = 1


class HighlightInline(admin.TabularInline):
    model = Highlight
    extra = 1


class CoHostInline(admin.TabularInline):
    model = CoHost
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "room_type", "is_super_host", "is_guest_favorite")
    search_fields = ("title", "description")
    list_filter = ("is_super_host", "is_guest_favorite", "room_type")
    inlines = [
        ImageInline,
        LocationDescriptionInline,
        HighlightInline,
        CoHostInline,
    ]


@admin.register(Coordinates)
class CoordinatesAdmin(ReadOnlyAdmin):
    list_display = ("property", "latitude", "longitude")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("property", "guest_satisfaction", "review_count")


@admin.register(HouseRules)
class HouseRulesAdmin(ReadOnlyAdmin):
    list_display = ("property",)


@admin.register(GeneralRule)
class GeneralRuleAdmin(admin.ModelAdmin):
    list_display = ("house_rules", "title")
    inlines = [GeneralRuleValueInline]


@admin.register(Host)
class HostAdmin(ReadOnlyAdmin):
    list_display = ("property", "name", "host_id")


@admin.register(SubDescription)
class SubDescriptionAdmin(admin.ModelAdmin):
    list_display = ("property", "title")


@admin.register(Amenity)
class AmenityAdmin(ReadOnlyAdmin):
    list_display = ("property", "title")
    inlines = [AmenityValueInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("property", "title", "url")


@admin.register(LocationDescription)
class LocationDescriptionAdmin(admin.ModelAdmin):
    list_display = ("property", "title")


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("property", "title")


@admin.register(CoHost)
class CoHostAdmin(admin.ModelAdmin):
    list_display = ("property", "name", "host_id")
