import secrets


def generate_urlsafe_token(size: int = 64) -> str:
    """Generate a cryptographically secure URL-safe token.

    :param size: Number of random bytes used to generate the token.
    :return: A URL-safe token.
    :raises TypeError: If ``size`` is not an integer.
    :raises ValueError: If ``size`` is not positive.
    """
    if isinstance(size, bool) or not isinstance(size, int):
        raise TypeError("token size must be an integer")
    if size <= 0:
        raise ValueError("token size must be positive")
    return secrets.token_urlsafe(size)
