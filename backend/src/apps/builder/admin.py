from django.contrib import admin

from apps.builder.forms import ThemeColorsWidget
from apps.builder.models import ThemeChoices, ColorSchemeChoices, Website


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
