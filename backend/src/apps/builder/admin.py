from django.contrib import admin

from apps.builder.forms import ThemeColorsWidget
from apps.builder.models import (
    ThemeChoices,
    ColorSchemeChoices,
    Website,
    Package,
    Promotion,
    StripeWebhookPayload,
    RegistrationOptions,
    LeadRegistration,
)


@admin.register(ThemeChoices)
class ThemeChoicesAdmin(admin.ModelAdmin):
    list_display = ("name", "preview_link", "icon_name")
    search_fields = ("name",)


@admin.register(ColorSchemeChoices)
class ColorSchemeChoicesAdmin(admin.ModelAdmin):
    list_display = ("name", "internal_name", "theme_colors")
    search_fields = ("name", "internal_name")

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "theme_colors":
            kwargs["widget"] = ThemeColorsWidget
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("domain_name", "theme", "color_scheme")
    list_filter = ("theme", "color_scheme")
    search_fields = ("domain_name",)


class PromotionInline(admin.TabularInline):
    model = Promotion
    extra = 1


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("label", "name", "amount", "frequency", "description")
    search_fields = ("name",)
    list_filter = ("name", "label", "frequency")
    inlines = [PromotionInline]


@admin.register(StripeWebhookPayload)
class StripeWebhookPayloadAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "payload",
    )
    search_fields = ("payload",)


class RegistrationOptionsInline(admin.TabularInline):
    model = RegistrationOptions
    extra = 0
    fields = ("promotion", "package", "paid_at", "expires_at")


@admin.register(LeadRegistration)
class LeadRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "phone_number",
        "theme",
        "color_scheme",
        "created_at",
    )
    list_filter = ("theme", "color_scheme", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone_number", "domain_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [RegistrationOptionsInline]

    fieldsets = (
        (
            "Contact Information",
            {"fields": ("email", "first_name", "last_name", "phone_number", "user")},
        ),
        ("Design Preferences", {"fields": ("theme", "color_scheme")}),
        ("Property Details", {"fields": ("listing_urls", "domain_name")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(RegistrationOptions)
class RegistrationOptionsAdmin(admin.ModelAdmin):
    list_display = ("lead_registration", "promotion", "package", "created_at")
    list_filter = ("promotion", "package", "created_at")
    search_fields = ("lead_registration__email",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Lead Information", {"fields": ("lead_registration",)}),
        ("Options", {"fields": ("promotion", "package")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "expires_at"),
                "classes": ("collapse",),
            },
        ),
        ("Paid", {"fields": ("paid_at",)}),
    )
