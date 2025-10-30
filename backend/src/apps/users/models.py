from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.users.utils import get_user_avatar_path


# Create your models here.
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
