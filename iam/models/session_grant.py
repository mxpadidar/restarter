import uuid

from django.db import models

from core.utils import get_current_datetime

from .user import User


class SessionGrant(models.Model):
    """Represent one renewable grant within an authenticated session.

    Each grant contains a refresh secret and belongs to a logical session identified
    by ``session_id``. During token rotation, the current grant is revoked and a new
    grant is created with the same ``session_id``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    user: User = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grants")  # type: ignore[reportAssignmentType]
    session_id = models.UUIDField(editable=False)
    secret_hash = models.CharField(max_length=64, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "session_grants"
        ordering = ("-issued_at", "-id")
        default_permissions = ()

        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                condition=models.Q(expires_at__gt=models.F("issued_at")),
                name="session_grant_expiry_after_issue",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(revoked_at__isnull=True)
                    | models.Q(revoked_at__gte=models.F("issued_at"))
                ),
                name="session_grant_revocation_after_issue",
            ),
            models.UniqueConstraint(
                fields=["session_id"],
                condition=models.Q(revoked_at__isnull=True),
                name="session_grant_one_unrevoked_per_session",
            ),
        ]
        indexes = [  # noqa: RUF012
            models.Index(
                fields=["user", "expires_at"],
                condition=models.Q(revoked_at__isnull=True),
                name="session_grant_active_user_idx",
            ),
        ]

    def __str__(self) -> str:
        """Return a human-readable identifier for the grant."""
        return f"{self.user.username} - {self.id.hex}"

    @property
    def is_active(self) -> bool:
        """Return whether the grant is unrevoked and unexpired."""
        return self.revoked_at is None and self.expires_at > get_current_datetime()

    def revoke(self) -> None:
        """Revoke an active grant.

        :raises ValueError: If the grant is already revoked or expired.
        """
        if not self.is_active:
            raise ValueError("cannot revoke an inactive grant")
        self.revoked_at = max(get_current_datetime(), self.issued_at)
        self.save(update_fields=["revoked_at"])
