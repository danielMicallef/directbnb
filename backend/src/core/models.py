from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractTrackedModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation time")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Update time"))

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")

        if isinstance(update_fields, list) and "updated_at" not in update_fields:
            update_fields.append("updated_at")
        super().save(*args, **kwargs)
