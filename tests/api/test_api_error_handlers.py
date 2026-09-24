from rest_framework import exceptions

from api.error_handlers import api_error_handler
from conf.request_ctx import bind_request_id
from core.errors import ConflictError


def test_custom_handler_returns_structured_application_error():
    """Application errors should become structured HTTP error responses."""
    response = api_error_handler(
        ConflictError("email is already registered", email="user@example.com"),
        {},
    )

    assert response is not None
    assert response.status_code == 409
    assert response.data == {
        "error": {
            "code": "conflict",
            "message": "email is already registered",
            "details": {"email": "user@example.com"},
        }
    }


def test_custom_handler_delegates_drf_exceptions():
    """Native DRF exceptions should use the common error response structure."""
    response = api_error_handler(exceptions.NotFound(), {})

    assert response is not None
    assert response.status_code == 404
    assert response.data == {
        "error": {
            "code": "not_found",
            "message": "Not found.",
            "details": {"detail": "Not found."},
        }
    }


def test_custom_handler_structures_validation_errors():
    """Validation errors should preserve field-level details."""
    response = api_error_handler(
        exceptions.ValidationError({"email": ["This field is required."]}),
        {},
    )

    assert response is not None
    assert response.status_code == 400
    assert response.data == {
        "error": {
            "code": "validation_error",
            "message": "An error occurred.",
            "details": {"email": ["This field is required."]},
        }
    }


def test_custom_handler_uses_server_error_status_for_unknown_code():
    """Unknown exceptions should return a generic error with a request ID."""
    with bind_request_id("request-123"):
        response = api_error_handler(ValueError("unexpected error"), {})

    assert response is not None
    assert response.status_code == 500
    assert response.data == {
        "error": {
            "code": "server_error",
            "message": "an unexpected error occurred.",
            "details": {"request_id": "request-123"},
        }
    }
