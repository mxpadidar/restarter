import dataclasses
from uuid import UUID

from core.rbac import Role


@dataclasses.dataclass(frozen=True, slots=True)
class AuthUser:
    """Authenticated API principal reconstructed from an access token."""

    user_id: UUID
    session_grant_id: UUID
    roles: set[Role]

    @property
    def is_anonymous(self) -> bool:
        """Return whether this principal represents an anonymous request."""
        return False

    @property
    def is_authenticated(self) -> bool:
        """Return whether this principal represents an authenticated request."""
        return True
