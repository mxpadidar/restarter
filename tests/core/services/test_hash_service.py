import pytest

from conf.container import Container


def test_hash_creates_valid_and_different_string(container: Container):
    """Tests that hash() produces a non-empty string that is different from
    the original plaintext."""
    plain_text = "a-secret-password-for-mxpadidar"
    hashed_text = container.hmac_hasher.hash(plain_text=plain_text)

    assert isinstance(hashed_text, str)
    assert hashed_text != ""
    assert hashed_text != plain_text


def test_hash_raises_errors_for_invalid_input(container: Container):
    """Tests that the public hash() method raises errors for invalid inputs
    like None or empty strings."""
    with pytest.raises(TypeError):
        container.hmac_hasher.hash(plain_text=None)  # type: ignore

    with pytest.raises(ValueError):
        container.hmac_hasher.hash(plain_text="")


def test_verify_handles_correct_and_incorrect_text(container: Container):
    """Tests that verify() returns True for the correct text and False for an incorrect one."""
    plain_text = "correct-password"
    hashed_text = container.hmac_hasher.hash(plain_text=plain_text)

    assert container.hmac_hasher.verify(plain_text=plain_text, expected_hash=hashed_text) is True
    assert (
        container.hmac_hasher.verify(plain_text="invalid-text", expected_hash=hashed_text) is False
    )
    assert (
        container.hmac_hasher.verify(plain_text=plain_text, expected_hash="wronghashedvalue")
        is False
    )


@pytest.mark.parametrize(
    "plain_text, expected_hash",
    [
        pytest.param("", "deadbeef", id="empty-val"),
        pytest.param("a-valid-password", "", id="empty-hash"),
    ],
)
def test_verify_invalid_cases(
    container: Container, plain_text: str | None, expected_hash: str | None
):
    """Combine invalid verify cases (type/empty inputs and malformed hash) into one parametrized test."""
    with pytest.raises(ValueError):
        container.hmac_hasher.verify(plain_text=plain_text, expected_hash=expected_hash)  # type: ignore


@pytest.mark.parametrize(
    "plain_text, expected_hash",
    [
        pytest.param(None, "deadbeef", id="plain-text-not-string"),
        pytest.param("a-valid-password", None, id="hash-not-string"),
    ],
)
def test_verify_rejects_non_string_inputs(
    container: Container, plain_text: str | None, expected_hash: str | None
):
    """Verification requires string inputs."""
    with pytest.raises(TypeError):
        container.hmac_hasher.verify(plain_text=plain_text, expected_hash=expected_hash)  # type: ignore
