from django.urls import path

from apps.builder import views

app_name = "builder"

urlpatterns = [
    # Booking wizard
    path("wizard/", views.BookingWizardView.as_view(), name="wizard"),
    path("wizard/back/", views.wizard_go_back, name="wizard_back"),
    path("wizard/reset/", views.wizard_reset, name="wizard_reset"),
    # Checkout
    path("checkout/<uuid:pk>", views.LeadRegistrationView.as_view(), name="checkout"),
    path(
        "checkout_success/<uuid:pk>",
        views.SuccessLeadRegistrationView.as_view(),
        name="checkout_success",
    ),
    path(
        "checkout_cancelled/<uuid:pk>",
        views.CancelLeadRegistrationView.as_view(),
        name="checkout_cancelled",
    ),
]
