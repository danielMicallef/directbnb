from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView

from apps.builder.models import LeadRegistration


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
