from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

from apps.builder.models import (
    LeadRegistration,
    Package,
    Promotion,
    RegistrationOptions,
)
from apps.builder.wizard_forms import (
    ThemeSelectionForm,
    ColorSchemeForm,
    BookingLinksForm,
    DomainNameForm,
    ContactDetailsForm,
    PackageSelectionForm,
    ReviewForm,
)


class LeadRegistrationView(DetailView):
    model = LeadRegistration

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.completed_at:
            return render(
                request,
                "builder/lead_already_completed.html",
                {"lead": self.object},
            )

        try:
            checkout_session = self.object.create_checkout_session()
            return HttpResponseRedirect(checkout_session.url)
        except (ValueError, Exception) as e:
            # Log the error properly in a real app
            return render(
                request,
                "builder/lead_payment_error.html",
                {"error_message": str(e)},
            )


class SuccessLeadRegistrationView(DetailView):
    model = LeadRegistration
    template_name = "builder/stripe/success.html"


class CancelLeadRegistrationView(DetailView):
    model = LeadRegistration
    template_name = "builder/stripe/cancelled.html"


class BookingWizardView(View):
    """Multi-step booking wizard with HTMX support"""

    FORMS = {
        1: ThemeSelectionForm,
        2: ColorSchemeForm,
        3: BookingLinksForm,
        4: DomainNameForm,
        5: ContactDetailsForm,
        6: PackageSelectionForm,
        7: ReviewForm,
    }

    TOTAL_STEPS = 7

    def get(self, request):
        """Display the wizard"""
        step = self.get_current_step(request)
        form = self.get_form(request, step)

        context = {
            "form": form,
            "step": step,
            "total_steps": self.TOTAL_STEPS,
            "wizard_data": self.get_wizard_data(request),
        }

        # If HTMX request, return partial
        if request.headers.get("HX-Request"):
            return render(request, "builder/wizard_step_partial.html", context)

        return render(request, "builder/booking_wizard.html", context)

    def post(self, request):
        """Handle form submission"""
        step = self.get_current_step(request)
        form = self.get_form(request, step, data=request.POST)

        if form.is_valid():
            # Save form data to session
            self.save_step_data(request, step, form.cleaned_data)

            # Handle step 5 (Contact Details) - Create/Update LeadRegistration
            if step == 5:
                lead_id = self.create_or_update_lead(request, form.cleaned_data)
                request.session["lead_registration_id"] = str(lead_id)

            # Move to next step or complete
            if step < self.TOTAL_STEPS:
                request.session["wizard_step"] = step + 1
            else:
                # Final step - process payment
                return self.complete_wizard(request)

            # Return next step via HTMX
            next_step = step + 1
            next_form = self.get_form(request, next_step)

            context = {
                "form": next_form,
                "step": next_step,
                "total_steps": self.TOTAL_STEPS,
                "wizard_data": self.get_wizard_data(request),
            }

            return render(request, "builder/wizard_step_partial.html", context)

        # Form invalid - return with errors
        context = {
            "form": form,
            "step": step,
            "total_steps": self.TOTAL_STEPS,
            "wizard_data": self.get_wizard_data(request),
        }

        return render(request, "builder/wizard_step_partial.html", context)

    def get_current_step(self, request):
        """Get current wizard step from session"""
        return request.session.get("wizard_step", 1)

    def get_form(self, request, step, data=None):
        """Get form instance for given step"""
        form_class = self.FORMS.get(step)
        if not form_class:
            return None

        # Get saved data for this step
        saved_data = self.get_step_data(request, step)

        # Pre-fill contact details for logged-in users
        if step == 5 and request.user.is_authenticated and not saved_data:
            saved_data = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": request.user.phone_number,
            }

        if data:
            return form_class(data)
        elif saved_data:
            return form_class(initial=saved_data)
        else:
            return form_class()

    def get_wizard_data(self, request):
        """Get all wizard data from session"""
        return request.session.get("wizard_data", {})

    def get_step_data(self, request, step):
        """Get data for specific step"""
        wizard_data = self.get_wizard_data(request)
        return wizard_data.get(f"step_{step}", {})

    def save_step_data(self, request, step, data):
        """Save step data to session"""
        wizard_data = self.get_wizard_data(request)

        # For step 6, add package details for display in step 7 BEFORE serialization
        if step == 6:
            total = Decimal("0.00")
            currency = "EUR"

            # Store package details
            if data.get("package"):
                package = data["package"]
                wizard_data["step_6_package_details"] = {
                    "name": package.name,
                    "amount": str(package.amount),
                    "currency": package.currency,
                }
                total += package.amount
                currency = package.currency

            # Store hosting details
            if data.get("hosting_plan"):
                hosting = data["hosting_plan"]
                wizard_data["step_6_hosting_details"] = {
                    "name": hosting.name,
                    "amount": str(hosting.amount),
                    "currency": hosting.currency,
                }
                total += hosting.amount

            # Store addon details
            if data.get("live_reviews"):
                addon = Package.objects.filter(
                    label=Package.LabelChoices.ADDON, name__icontains="reviews"
                ).first()
                if addon:
                    wizard_data["step_6_addon_details"] = {
                        "name": addon.name,
                        "amount": str(addon.amount),
                        "currency": addon.currency,
                    }
                    total += addon.amount

            wizard_data["step_6_total"] = {
                "amount": str(total),
                "currency": currency,
            }

        # Convert model instances to IDs for JSON serialization
        serialized_data = {}
        for key, value in data.items():
            if hasattr(value, "pk"):
                serialized_data[key] = value.pk
            elif isinstance(value, bool):
                serialized_data[key] = value
            else:
                serialized_data[key] = str(value) if value else None

        wizard_data[f"step_{step}"] = serialized_data
        request.session["wizard_data"] = wizard_data
        request.session.modified = True

    def create_or_update_lead(self, request, contact_data):
        """Create or update LeadRegistration"""
        wizard_data = self.get_wizard_data(request)

        # Get booking links
        booking_links = []
        step_3_data = wizard_data.get("step_3", {})
        airbnb_link = step_3_data.get("airbnb_link")
        booking_com_link = step_3_data.get("booking_com_link")
        if airbnb_link:
            booking_links.append(airbnb_link)
        if booking_com_link:
            booking_links.append(booking_com_link)

        # Get or create lead
        lead_id = request.session.get("lead_registration_id")
        if lead_id:
            try:
                lead = LeadRegistration.objects.get(id=lead_id)
            except LeadRegistration.DoesNotExist:
                lead = None
        else:
            lead = None

        # Prepare lead data
        lead_data = {
            "email": contact_data["email"],
            "first_name": contact_data["first_name"],
            "last_name": contact_data["last_name"],
            "phone_number": contact_data["phone"],
            "listing_urls": booking_links if booking_links else [],
            "domain_name": wizard_data.get("step_4", {}).get("domain_name", ""),
        }

        # Add theme and color scheme if selected
        theme_id = wizard_data.get("step_1", {}).get("theme")
        if theme_id:
            lead_data["theme_id"] = theme_id

        color_scheme_id = wizard_data.get("step_2", {}).get("color_scheme")
        if color_scheme_id:
            lead_data["color_scheme_id"] = color_scheme_id

        # Add user if logged in
        if request.user.is_authenticated:
            lead_data["user"] = request.user

        if lead:
            # Update existing lead
            for key, value in lead_data.items():
                setattr(lead, key, value)
            lead.save()
        else:
            # Create new lead
            lead = LeadRegistration.objects.create(**lead_data)

        return lead.id

    def complete_wizard(self, request):
        """Complete wizard and create checkout session"""
        wizard_data = self.get_wizard_data(request)
        lead_id = request.session.get("lead_registration_id")

        if not lead_id:
            messages.error(request, "Session expired. Please start again.")
            return redirect("builder:wizard")

        try:
            lead = LeadRegistration.objects.get(id=lead_id)

            # Get package selections from step 6
            step_6_data = wizard_data.get("step_6", {})
            package_id = step_6_data.get("package")
            hosting_id = step_6_data.get("hosting_plan")
            live_reviews = step_6_data.get("live_reviews", False)

            # Get step 7 data
            step_7_data = wizard_data.get("step_7", {})
            micro_invest = step_7_data.get("micro_invest", False)

            # Create registration options for builder package
            if package_id:
                package = Package.objects.get(pk=package_id)
                # Check for active promotion
                promotion = Promotion.objects.filter(
                    package=package,
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date(),
                ).first()

                RegistrationOptions.objects.create(
                    lead_registration=lead,
                    package=package,
                    promotion=promotion
                    if promotion and promotion.is_promotion_available()
                    else None,
                )

            # Create registration option for hosting
            if hosting_id:
                hosting = Package.objects.get(pk=hosting_id)
                RegistrationOptions.objects.create(
                    lead_registration=lead, package=hosting
                )

            # Create registration option for live reviews addon
            if live_reviews:
                addon = Package.objects.filter(
                    label=Package.LabelChoices.ADDON, name__icontains="reviews"
                ).first()
                if addon:
                    RegistrationOptions.objects.create(
                        lead_registration=lead, package=addon
                    )

            # Update lead with micro invest preference
            if micro_invest:
                extra_req = lead.extra_requirements or {}
                extra_req["microInvest"] = True
                lead.extra_requirements = extra_req
                lead.save(update_fields=["extra_requirements"])

            # Create Stripe checkout session
            checkout_session = lead.create_checkout_session()

            # Clear wizard data
            request.session.pop("wizard_data", None)
            request.session.pop("wizard_step", None)

            # Handle HTMX requests with HX-Redirect header
            if request.headers.get("HX-Request"):
                response = HttpResponse(status=200)
                response["HX-Redirect"] = checkout_session.url
                return response

            # Regular redirect for non-HTMX requests
            return HttpResponseRedirect(checkout_session.url)

        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect("builder:wizard")

    def wizard_go_back(self, request):
        """Handle back button - HTMX endpoint"""
        step = self.get_current_step(request)
        if step > 1:
            request.session["wizard_step"] = step - 1
            return self.get(request)
        return self.get(request)


def wizard_go_back(request):
    """HTMX endpoint for going back a step"""
    step = request.session.get("wizard_step", 1)
    if step > 1:
        request.session["wizard_step"] = step - 1
    return redirect("builder:wizard")


def wizard_reset(request):
    """Reset wizard session data"""
    request.session.pop("wizard_data", None)
    request.session.pop("wizard_step", None)
    request.session.pop("lead_registration_id", None)
    return redirect("builder:wizard")
