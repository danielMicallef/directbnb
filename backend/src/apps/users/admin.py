from django.contrib import admin
from apps.users.models import BNBUser, UserToken
from apps.builder.models import LeadRegistration, RegistrationOptions


@admin.register(BNBUser)
class BNBUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_email_confirmed",
        "registered_at",
    )
    list_filter = ("is_active", "is_staff", "is_email_confirmed", "registered_at")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("-registered_at",)
    readonly_fields = ("registered_at",)


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "is_expired")
    list_filter = ("created_at",)
    search_fields = ("user__email", "token")
    readonly_fields = ("token", "created_at", "updated_at")


class RegistrationOptionsInline(admin.TabularInline):
    model = RegistrationOptions
    extra = 0
    fields = ("promotion", "package")


@admin.register(LeadRegistration)
class LeadRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
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
            {"fields": ("email", "first_name", "last_name", "phone_number")},
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
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
