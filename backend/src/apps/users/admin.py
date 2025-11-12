from django.contrib import admin
from apps.users.models import BNBUser, UserToken


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
