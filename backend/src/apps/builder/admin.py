from django.contrib import admin
from apps.builder.models import ThemeChoices, ColorSchemeChoices, Website


@admin.register(ThemeChoices)
class ThemeChoicesAdmin(admin.ModelAdmin):
    list_display = ("name", "preview_link", "icon_name")
    search_fields = ("name",)


@admin.register(ColorSchemeChoices)
class ColorSchemeChoicesAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    search_fields = ("name",)


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("domain_name", "theme", "color_scheme")
    list_filter = ("theme", "color_scheme")
    search_fields = ("domain_name",)
