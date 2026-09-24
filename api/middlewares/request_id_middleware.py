"""Middleware for generating and propagating request IDs."""

import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from conf.request_ctx import bind_request_id


class RequestIDMiddleware:
    """Bind a request ID while downstream request processing runs."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = uuid.uuid4().hex

        with bind_request_id(request_id):
            response = self.get_response(request)

        response["x-request-id"] = request_id
        return response
