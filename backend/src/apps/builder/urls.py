from django.urls import path

from apps.builder import views

app_name = "builder"

urlpatterns = [
    path("checkout/<uuid:pk>", views.LeadRegistrationView.as_view(), name="checkout"),
    path("checkout_success/<uuid:pk>", views.SuccessLeadRegistrationView.as_view(), name="checkout_success"),
    path("checkout_cancelled/<uuid:pk>", views.CancelLeadRegistrationView.as_view(), name="checkout_cancelled"),
]
