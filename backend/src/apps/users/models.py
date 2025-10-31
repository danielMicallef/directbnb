from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template.loader import render_to_string

from phonenumber_field.modelfields import PhoneNumberField

from apps.users.utils import get_user_avatar_path
from apps.users.managers import UserManager
from core.models import AbstractTrackedModel


class BNBUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="Email",
        unique=True,
        max_length=255,
    )
    first_name = models.CharField(
        verbose_name="First Name",
        max_length=255,
    )
    last_name = models.CharField(
        verbose_name="Last Name",
        max_length=255,
    )
    phone_number = PhoneNumberField(verbose_name="Phone Number", blank=True, null=True)
    avatar = models.ImageField(
        verbose_name="Avatar", null=True, blank=True, upload_to=get_user_avatar_path
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_email_confirmed = models.BooleanField(_("confirmed email"), default=False)
    registered_at = models.DateTimeField(_("registered at"), auto_now_add=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_activation_email(self):
        token = self.create_user_token()
        verification_url = reverse("users:verify_email", kwargs={"token": token})
        full_verification_url = f"{settings.SITE_URL}{verification_url}"

        context = {
            "user": self,
            "verification_url": full_verification_url,
        }
        body = render_to_string("users/emails/verify_email.html", context)
        self.email_user(
            subject=_("Activate Your Account"),
            message=body,
        )

    def create_user_token(self):
        ut = UserToken(user=self)
        ut.save()
        return ut.token


class UserToken(AbstractTrackedModel):
    MAX_HOURS_VALID = 24

    user = models.ForeignKey(BNBUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, editable=False, unique=True)

    @property
    def is_expired(self):
        from datetime import timedelta
        from django.utils import timezone
        return (timezone.now() - self.created_at) > timedelta(hours=self.MAX_HOURS_VALID)
