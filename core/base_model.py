"""Shared abstract Django models."""

import uuid

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Provide common identifiers, timestamps, soft deletion, and model defaults."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        default_permissions = ()
        ordering = ("-created_at", "-id")

    def soft_delete(self) -> None:
        """Mark the model as deleted while preserving its original deletion time."""
        if self.deleted_at is not None:
            raise ValueError("record has already been deleted")
        self.deleted_at = timezone.now()
        self.save(update_fields=("deleted_at",))
