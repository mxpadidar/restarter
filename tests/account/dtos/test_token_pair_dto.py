from datetime import UTC, datetime
from uuid import uuid4

import pytest

from account.dtos import TokenPair


def test_token_pair_creates_and_parses_a_refresh_token():
    grant_id = uuid4()
    expires_at = datetime(2026, 9, 27, 12, tzinfo=UTC)

    token_pair = TokenPair.create(
        access_token="access-token",
        refresh_secret="refresh-secret",
        grant_id=grant_id,
        access_expires_at=expires_at,
    )

    assert token_pair.access_token == "access-token"
    assert token_pair.refresh_token == f"{grant_id.hex}:refresh-secret"
    assert token_pair.expires_at == expires_at
    assert TokenPair.parse_refresh_token(token_pair.refresh_token) == (grant_id, "refresh-secret")


@pytest.mark.parametrize(
    "refresh_token", ["", "grant-id", "grant-id:", ":secret", "not-a-uuid:secret", None]
)
def test_token_pair_rejects_an_invalid_refresh_token(refresh_token: object):
    with pytest.raises(ValueError):
        TokenPair.parse_refresh_token(refresh_token)  # type: ignore[arg-type]
