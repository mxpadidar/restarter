import uuid

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from api.middlewares import RequestIDMiddleware
from conf.request_ctx import bind_request_id, get_request_id


def test_request_without_id_gets_generated_id_in_context_and_response():
    """A missing request ID should be generated, bound, and returned."""
    active_request_ids: list[str | None] = []

    def get_response(*_) -> HttpResponse:
        active_request_ids.append(get_request_id())
        return HttpResponse("ok")

    request = RequestFactory().get("/api/test")
    response = RequestIDMiddleware(get_response)(request)
    request_id = response.headers["X-Request-ID"]

    assert uuid.UUID(request_id).hex == request_id
    assert active_request_ids == [request_id]
    assert get_request_id() is None
    assert not hasattr(request, "request_id")


def test_previous_request_context_is_restored_after_downstream_error():
    """A downstream exception should not leak or discard context values."""

    def get_response(*_) -> HttpResponse:
        assert get_request_id() is not None
        raise RuntimeError("request failed")

    middleware = RequestIDMiddleware(get_response)
    request = RequestFactory().get("/api/test")

    with bind_request_id("outer"):
        with pytest.raises(RuntimeError):
            middleware(request)

        assert get_request_id() == "outer"

    assert get_request_id() is None
