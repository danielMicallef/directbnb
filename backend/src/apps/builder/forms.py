import json
from django import forms


class ThemeColorsWidget(forms.Widget):
    template_name = "builder/theme_colors_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        try:
            context["widget"]["colors"] = json.loads(value) if value else []
        except (TypeError, json.JSONDecodeError):
            context["widget"]["colors"] = []

        context["widget"]["color_name_choices"] = [
            "base",
            "primary",
            "secondary",
            "accent",
            "neutral",
            "info",
            "success",
            "warning",
            "error",
        ]
        return context

    def value_from_datadict(self, data, files, name):
        color_names = data.getlist(f"{name}_name")
        color_values = data.getlist(f"{name}_value")

        colors = [
            {"name": name, "value": value}
            for name, value in zip(color_names, color_values)
            if name and value
        ]
        return json.dumps(colors)
