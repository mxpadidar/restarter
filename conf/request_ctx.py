"""Request context management for logging."""

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    """Return the request ID for the current execution context.

    :return: The active request ID, or ``None`` outside a request.
    """
    return _request_id.get()


@contextmanager
def bind_request_id(request_id: str) -> Generator[None]:
    """Temporarily bind a request ID to the current execution context.

    :param request_id: Request ID to make available to application logs.
    """
    token = _request_id.set(request_id)

    try:
        yield

    finally:
        _request_id.reset(token)
