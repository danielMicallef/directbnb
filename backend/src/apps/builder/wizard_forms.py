from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import RadioSelect
from phonenumber_field.formfields import PhoneNumberField

from apps.builder.models import ThemeChoices, ColorSchemeChoices, Package


class ThemeRadioSelect(RadioSelect):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # Add the model instance to the option context
        if value:
            try:
                theme = value.instance
                option["icon_name"] = theme.icon_name
                option["preview_link"] = theme.preview_link
            except ThemeChoices.DoesNotExist:
                option["icon_name"] = None
                option["preview_link"] = None
        return option


class ColorSchemeRadioSelect(RadioSelect):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # Add the color scheme theme_colors to the option context
        if value:
            try:
                color_scheme = value.instance
                option["theme_colors"] = color_scheme.theme_colors
            except (ColorSchemeChoices.DoesNotExist, ValueError, TypeError, AttributeError):
                option["theme_colors"] = []

        return option

    def optgroups(self, name, value, attrs=None):
        """Override to pass color scheme data"""
        groups = super().optgroups(name, value, attrs)
        # Enhance each option with theme_colors
        for group_name, options, index in groups:
            for option in options:
                option_value = option.get("value")
                if option_value:
                    try:
                        # Extract the actual PK value from ModelChoiceIteratorValue
                        if hasattr(option_value, 'value'):
                            pk = option_value.value
                        else:
                            pk = option_value
                        
                        color_scheme = ColorSchemeChoices.objects.get(pk=pk)
                        option["theme_colors"] = color_scheme.theme_colors
                    except (ColorSchemeChoices.DoesNotExist, ValueError, TypeError, AttributeError):
                        option["theme_colors"] = []
        return groups


class PackageRadioSelect(RadioSelect):
    def optgroups(self, name, value, attrs=None):
        """Override to pass package data"""
        groups = super().optgroups(name, value, attrs)
        # Enhance each option with package details
        for group_name, options, index in groups:
            for option in options:
                if option.get("value"):
                    try:
                        package = Package.objects.get(pk=option["value"])
                        option["package_name"] = package.name
                        option["package_description"] = package.description
                        option["package_amount"] = str(package.amount)
                        option["package_currency"] = package.currency
                        option["package_frequency"] = package.frequency
                        option["package_frequency_display"] = (
                            package.get_frequency_display()
                        )
                    except (Package.DoesNotExist, ValueError, TypeError):
                        option["package_name"] = option.get("label", "")
                        option["package_description"] = ""
                        option["package_amount"] = "0"
                        option["package_currency"] = "EUR"
        return groups


class BaseWizardForm(forms.Form):
    """Base form for wizard steps"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add DaisyUI classes to all form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({"class": "input input-bordered w-full"})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(
                    {"class": "textarea textarea-bordered w-full"}
                )
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "select select-bordered w-full"})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "checkbox"})


class ThemeSelectionForm(BaseWizardForm):
    """Step 1: Theme Selection"""

    theme = forms.ModelChoiceField(
        queryset=ThemeChoices.objects.all(),
        required=True,
        empty_label=None,
        widget=ThemeRadioSelect(attrs={"class": "radio radio-primary"}),
        label="Choose Your Theme",
    )


class ColorSchemeForm(BaseWizardForm):
    """Step 2: Color Scheme Selection"""

    color_scheme = forms.ModelChoiceField(
        queryset=ColorSchemeChoices.objects.all(),
        required=True,
        empty_label=None,
        widget=ColorSchemeRadioSelect(attrs={"class": "radio radio-primary"}),
        label="Select your Color Preset",
    )


class BookingLinksForm(BaseWizardForm):
    """Step 3: Booking Links"""

    airbnb_link = forms.URLField(
        required=False,
        label="Airbnb Link",
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://www.airbnb.com/rooms/...",
                "class": "input input-bordered w-full",
            }
        ),
    )
    booking_com_link = forms.URLField(
        required=False,
        label="Booking.com Link (Optional)",
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://www.booking.com/...",
                "class": "input input-bordered w-full",
            }
        ),
    )
    not_listed = forms.BooleanField(
        required=False,
        label="My apartment is not currently listed. I will add data manually.",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        not_listed = cleaned_data.get("not_listed")
        airbnb_link = cleaned_data.get("airbnb_link")
        booking_com_link = cleaned_data.get("booking_com_link")

        if not not_listed and not airbnb_link and not booking_com_link:
            raise ValidationError(
                "Please enter at least one booking URL or select that your apartment is not listed."
            )

        # Validate Airbnb URL
        if airbnb_link and "airbnb." not in airbnb_link.lower():
            raise ValidationError({"airbnb_link": "Please enter a valid Airbnb URL."})

        # Validate Booking.com URL
        if booking_com_link and "booking." not in booking_com_link.lower():
            raise ValidationError(
                {"booking_com_link": "Please enter a valid Booking.com URL."}
            )

        return cleaned_data


class DomainNameForm(BaseWizardForm):
    """Step 4: Domain Name (Optional)"""

    domain_name = forms.CharField(
        required=False,
        label="Add Your Domain Name",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "myamazingvilla.com",
                "class": "input input-bordered w-full",
            }
        ),
        help_text="Pick a memorable domain for your direct booking website. We can help you register it! (Optional)",
    )
    skip_domain = forms.BooleanField(
        required=False,
        label="I don't have a domain name right now.",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
    )


class ContactDetailsForm(BaseWizardForm):
    """Step 5: Contact Details"""

    first_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "John", "class": "input input-bordered w-full"}
        ),
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Doe", "class": "input input-bordered w-full"}
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "john@example.com",
                "class": "input input-bordered w-full",
            }
        ),
    )
    phone = PhoneNumberField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "+1 (555) 000-0000",
                "class": "input input-bordered w-full",
            }
        ),
    )
    # Honeypot field for spam prevention
    confirm_email = forms.EmailField(required=False, widget=forms.HiddenInput())

    def clean_confirm_email(self):
        """If honeypot field is filled, it's likely a bot"""
        confirm_email = self.cleaned_data.get("confirm_email")
        if confirm_email:
            raise ValidationError("Invalid submission detected.")
        return confirm_email


class PackageSelectionForm(BaseWizardForm):
    """Step 6: Package and Hosting Selection"""

    package = forms.ModelChoiceField(
        queryset=Package.objects.filter(label=Package.LabelChoices.BUILDER),
        required=True,
        empty_label=None,
        widget=PackageRadioSelect(attrs={"class": "radio radio-primary"}),
        label="Choose Your Package",
    )
    hosting_plan = forms.ModelChoiceField(
        queryset=Package.objects.filter(label=Package.LabelChoices.HOSTING),
        required=True,
        empty_label=None,
        widget=PackageRadioSelect(attrs={"class": "radio radio-primary"}),
        label="Select Hosting Plan",
    )
    live_reviews = forms.BooleanField(
        required=False,
        label="Live Reviews Integration",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store addon info for template access
        self.addon = Package.objects.filter(
            label=Package.LabelChoices.ADDON, name__icontains="reviews"
        ).first()


class ReviewForm(BaseWizardForm):
    """Step 7: Review and Confirm"""

    micro_invest = forms.BooleanField(
        required=False,
        label="Interested to apply for up to 65% refund through the micro invest scheme",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="I accept the terms and conditions",
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),
        error_messages={
            "required": "You must accept the terms and conditions to proceed."
        },
    )
