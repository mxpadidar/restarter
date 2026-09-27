import re

import pytest

from core.utils import generate_urlsafe_token


def test_generate_urlsafe_token_returns_unique_urlsafe_tokens():
    token = generate_urlsafe_token()

    assert token != generate_urlsafe_token()
    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


@pytest.mark.parametrize("size", [0, -1])
def test_generate_urlsafe_token_rejects_non_positive_sizes(size: int):
    with pytest.raises(ValueError):
        generate_urlsafe_token(size)


@pytest.mark.parametrize("size", [True, "64", None])
def test_generate_urlsafe_token_rejects_non_integer_sizes(size: object):
    with pytest.raises(TypeError):
        generate_urlsafe_token(size)  # type: ignore
