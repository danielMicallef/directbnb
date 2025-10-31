from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, FormView, TemplateView
from django import forms

from apps.users.forms import EmailAuthenticationForm, RegistrationForm
from apps.users.models import BNBUser, UserToken


from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "users/home.html"


class RegisterView(CreateView):
    model = BNBUser
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Registration successful! Please check your email to verify your account.")
        )
        return response


class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.get_user()

        # Check if email is confirmed
        if not user.is_email_confirmed:
            messages.error(
                self.request,
                _("Please verify your email address before logging in. Check your inbox for the verification link.")
            )
            return self.form_invalid(form)

        # Proceed with normal login
        return super().form_valid(form)


def verify_email(request, token):
    user_token = get_object_or_404(UserToken, token=token)

    # Check if token is expired
    if user_token.is_expired:
        messages.error(request, _("This verification link has expired. Please request a new one."))
        user_token.delete()
        return redirect("users:login")

    user = user_token.user

    if user.is_email_confirmed:
        messages.warning(request, _("Your email has already been confirmed."))
    else:
        user.is_email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(request, _("Your email has been confirmed. You can now log in."))

    user_token.delete()
    return redirect("users:login")


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control'
        })
    )


class ResendVerificationEmailView(FormView):
    template_name = 'registration/resend_verification.html'
    form_class = ResendVerificationEmailForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']

        try:
            user = BNBUser.objects.get(email=email)

            if user.is_email_confirmed:
                messages.info(
                    self.request,
                    _("This email is already verified. You can log in now.")
                )
            else:
                # Delete old tokens for this user
                UserToken.objects.filter(user=user).delete()

                # Send new verification email
                user.send_activation_email()

                messages.success(
                    self.request,
                    _("Verification email has been sent. Please check your inbox.")
                )
        except BNBUser.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(
                self.request,
                _("If an account exists with this email, a verification link has been sent.")
            )

        return super().form_valid(form)
