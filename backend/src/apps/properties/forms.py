from django import forms
from django.forms import inlineformset_factory

from .models import (
    Property,
    Coordinates,
    Rating,
    HouseRules,
    Host,
    SubDescription,
    Amenity,
    AmenityValue,
    Image,
    LocationDescription,
    Highlight,
    CoHost,
)


class PropertyForm(forms.ModelForm):
    """Form for editing main property details"""

    class Meta:
        model = Property
        fields = [
            "room_type",
            "is_super_host",
            "home_tier",
            "person_capacity",
            "is_guest_favorite",
            "description",
            "title",
            "language",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "room_type": forms.TextInput(attrs={"placeholder": "e.g., Entire home/apt"}),
            "title": forms.TextInput(attrs={"placeholder": "Property title"}),
        }


class CoordinatesForm(forms.ModelForm):
    """Form for editing coordinates"""

    class Meta:
        model = Coordinates
        fields = ["latitude", "longitude"]
        widgets = {
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }


class RatingForm(forms.ModelForm):
    """Form for editing ratings"""

    class Meta:
        model = Rating
        fields = [
            "accuracy",
            "checking",
            "cleanliness",
            "communication",
            "location",
            "value",
            "guest_satisfaction",
            "review_count",
        ]
        widgets = {
            "accuracy": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "checking": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "cleanliness": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "communication": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "location": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "value": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
            "guest_satisfaction": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "5"}),
        }


class HouseRulesForm(forms.ModelForm):
    """Form for editing house rules"""

    class Meta:
        model = HouseRules
        fields = ["additional"]
        widgets = {
            "additional": forms.Textarea(attrs={"rows": 4}),
        }


class HostForm(forms.ModelForm):
    """Form for editing host information"""

    class Meta:
        model = Host
        fields = ["host_id", "name"]


class SubDescriptionForm(forms.ModelForm):
    """Form for editing sub description"""

    class Meta:
        model = SubDescription
        fields = ["title", "items"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g., Entire rental unit"}),
            "items": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Enter items as JSON array, e.g., [\"6 guests\", \"2 bedrooms\"]",
                }
            ),
        }


class ImageForm(forms.ModelForm):
    """Form for editing images"""

    class Meta:
        model = Image
        fields = ["title", "url"]
        widgets = {
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }


class LocationDescriptionForm(forms.ModelForm):
    """Form for editing location descriptions"""

    class Meta:
        model = LocationDescription
        fields = ["title", "content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3}),
        }


class HighlightForm(forms.ModelForm):
    """Form for editing highlights"""

    class Meta:
        model = Highlight
        fields = ["title", "subtitle", "icon"]


# Create formsets for one-to-many relationships
ImageFormSet = inlineformset_factory(
    Property,
    Image,
    form=ImageForm,
    extra=1,
    can_delete=True,
)

LocationDescriptionFormSet = inlineformset_factory(
    Property,
    LocationDescription,
    form=LocationDescriptionForm,
    extra=1,
    can_delete=True,
)

HighlightFormSet = inlineformset_factory(
    Property,
    Highlight,
    form=HighlightForm,
    extra=1,
    can_delete=True,
)
