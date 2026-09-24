"""Middleware that logs HTTP request and response details."""

import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from loguru import logger

from conf.request_ctx import get_request_id

EXCLUDED_PATHS = {"/docs/", "/schema/", "/favicon.ico"}


class RequestLoggingMiddleware:
    """Emit one Loguru access event for each HTTP request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path in EXCLUDED_PATHS:
            return self.get_response(request)

        started_at = time.perf_counter()

        try:
            response = self.get_response(request)
        except Exception:
            self._log_request(
                request=request,
                status_code=500,
                duration_ms=self._duration_ms(started_at),
                level="ERROR",
                exception=True,
            )
            raise

        self._log_request(
            request=request,
            status_code=response.status_code,
            duration_ms=self._duration_ms(started_at),
            level=self._log_level(response.status_code),
        )
        return response

    def _duration_ms(self, started_at: float) -> float:
        """Return elapsed request time in milliseconds."""
        return (time.perf_counter() - started_at) * 1000

    def _log_request(
        self,
        *,
        request: HttpRequest,
        status_code: int,
        duration_ms: float,
        level: str,
        exception: bool = False,
    ) -> None:
        """Log request details as structured Loguru fields."""
        event = logger.patch(lambda record: record.update(module="http.request")).bind(
            request_id=get_request_id(),
            method=request.method,
            path=request.path,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        message = (
            f"{request.method} {request.path} | status={status_code} | duration={duration_ms:.2f}ms"
        )
        if exception:
            event.exception(message)
        else:
            event.log(level, message)

    def _log_level(self, status_code: int) -> str:
        """Return the Loguru level for an HTTP status code."""
        if status_code >= 500:
            return "ERROR"
        if status_code >= 400:
            return "WARNING"
        return "INFO"
