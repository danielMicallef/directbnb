from uuid import uuid4

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from apps.users.models import UserToken


def verify_email(request, token):
    user_token = get_object_or_404(UserToken, token=token)
    user = user_token.user

    if user.is_email_confirmed:
        messages.warning(request, "Your email has already been confirmed.")
    else:
        user.is_email_confirmed = True
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been confirmed. You can now log in.")

    user_token.delete()
    return redirect("users:login")