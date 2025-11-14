from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, FormView, TemplateView
from django import forms

from apps.users.forms import EmailAuthenticationForm, RegistrationForm
from apps.users.models import BNBUser, UserToken


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from apps.users.forms import SetInitialPasswordForm


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "users/home.html"


class RegisterView(CreateView):
    model = BNBUser
    form_class = RegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _(
                "Registration successful! Please check your email to verify your account."
            ),
        )
        return response


class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        user = form.get_user()

        # Check if email is confirmed
        if not user.is_email_confirmed:
            messages.error(
                self.request,
                _(
                    "Please verify your email address before logging in. Check your inbox for the verification link."
                ),
            )
            return self.form_invalid(form)

        # Proceed with normal login
        return super().form_valid(form)


def verify_email(request, token):
    user_token = get_object_or_404(UserToken, token=token)

    # Check if token is expired
    if user_token.is_expired:
        messages.error(
            request, _("This verification link has expired. Please request a new one.")
        )
        user_token.delete()
        return redirect("users:login")

    user = user_token.user

    if user.is_email_confirmed:
        messages.warning(request, _("Your email has already been confirmed."))
    else:
        user.is_email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(
            request, _("Your email has been confirmed. You can now log in.")
        )

    user_token.delete()

    if user.has_usable_password():
        return redirect("users:login")

    # Redirect to set initial password
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return redirect(
        reverse(
            "users:set_initial_password", kwargs={"uidb64": uid, "token": token}
        )
    )


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Email address", "class": "form-control"}
        ),
    )


class ResendVerificationEmailView(FormView):
    template_name = "registration/resend_verification.html"
    form_class = ResendVerificationEmailForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = BNBUser.objects.filter(email=email).first()
        if not user:
            messages.success(
                self.request,
                _(
                    "If an account exists with this email, a verification link has been sent."
                ),
            )
            return super().form_valid(form)

        if user.is_email_confirmed:
            user.send_email_is_verified()
            if not user.has_usable_password():
                # Redirect to set initial password
                url = user.get_reset_password_url()
                return redirect(url)

            messages.info(
                self.request,
                message=_("This email is already verified. You can log in now."),
            )
        else:
            token = user.refresh_user_token()
            user.send_activation_email(token)

            messages.success(
                self.request,
                _("Verification email has been sent. Please check your inbox."),
            )
        return super().form_valid(form)


class SetInitialPasswordView(PasswordResetConfirmView):
    form_class = SetInitialPasswordForm
    template_name = "registration/set_initial_password.html"
    success_url = reverse_lazy("users:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Your password has been set. You can now log in."))
        return redirect(self.success_url)


class BnbPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "users/emails/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")


class BnbPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class BnbPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class BnbPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
