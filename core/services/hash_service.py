import hashlib
import hmac
import secrets
from typing import Final


class HMACSHA256Hasher:
    """HMAC-SHA256 implementation of the HashService protocol.

    Uses the built-in hashlib/hmac modules. Suitable for MAC signing and
    verification of short messages or tokens — not password hashing."""

    def __init__(self, key: bytes) -> None:
        """Initialize the hasher with a secret key."""
        if not isinstance(key, bytes) or not key:
            raise ValueError("HMAC key must be a non-empty byte string")

        self._key: Final[bytes] = key

    def hash(self, plain_text: str) -> str:
        """Compute an HMAC-SHA256 signature.

        :param plain_text: The input value to sign.
        :raises TypeError: If `plain_text` is not a string.
        :raises ValueError: If `plain_text` is empty.
        :return: Hex-encoded HMAC digest."""
        if not isinstance(plain_text, str):
            raise TypeError("plain_text must be a string")
        if not plain_text:
            raise ValueError("plain_text cannot be empty")

        return hmac.new(self._key, plain_text.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, *, plain_text: str, expected_hash: str) -> bool:
        """Verify a value against an expected HMAC-SHA256 digest.

        :param plain_text: The original plain-text value.
        :param expected_hash: The expected HMAC digest (hex string).
        :raises TypeError: If inputs are not strings.
        :raises ValueError: If either input is empty.
        :return: True if they match, False otherwise.
        """
        if not isinstance(plain_text, str) or not isinstance(expected_hash, str):
            raise TypeError("plain_text and expected_hash must be strings")
        if not plain_text or not expected_hash:
            raise ValueError("plain_text and expected_hash cannot be empty")

        expected = self.hash(plain_text)
        return secrets.compare_digest(expected, expected_hash)
