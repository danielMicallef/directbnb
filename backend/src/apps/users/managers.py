from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from loguru import logger


class UserManager(BaseUserManager):
    def create(self, *args, password=None, **kwargs):
        # Ignores password on purpose. Password can only be set after creation.
        return self.create_user(*args, **kwargs)

    def _create_user(
        self,
        email,
        password,
        is_staff,
        is_superuser,
        is_active=False,
        **extra_fields,
    ):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError("The given email must be set.")

        user = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_login=timezone.now(),
            registered_at=timezone.now(),
            **extra_fields,
        )

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)
        is_superuser = extra_fields.pop("is_superuser", False)
        user = self._create_user(
            email,
            password,
            is_staff,
            is_superuser,
            **extra_fields,
        )

        logger.info("Sending activation email to %s", user.email)
        user.send_activation_email()

        return user

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(
            email,
            password,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **extra_fields,
        )
