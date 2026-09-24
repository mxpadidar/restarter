"""Build consistent API responses for application and DRF exceptions."""

from typing import Any

from django.utils.translation import gettext as _
from loguru import logger
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler

from conf.request_ctx import get_request_id
from core.errors import BaseError, ErrorCode


def build_error_response(*, code: str, message: str, status_code: int, details: Any) -> Response:
    """Build the common API error response envelope.

    :param code: Stable machine-readable error code.
    :param message: Human-readable error summary.
    :param details: Error-specific details, such as field validation errors.
    :param status_code: HTTP status code for the response.
    :return: Structured DRF error response.
    """
    return Response(
        {
            "error": {"code": code, "message": message, "details": details},
        },
        status=status_code,
    )


def get_error_status_code(error_code: ErrorCode) -> int:
    """Return the HTTP status code corresponding to an application error code.

    :param error_code: Application error code.
    :return: HTTP status code.
    """

    ERROR_STATUS_CODES = {
        ErrorCode.SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.CONFLICT: status.HTTP_409_CONFLICT,
        ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
        ErrorCode.AUTHENTICATION_FAILED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.OPERATION_NOT_ALLOWED: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }

    status_code = ERROR_STATUS_CODES.get(error_code)
    if status_code is not None:
        return status_code

    logger.warning("unhandled application error code: {}", error_code)
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def core_error_handler(exc: BaseError, context: dict) -> Response:
    """Convert an application error into a structured API response.

    :param exc: Application error raised by the core layer.
    :param context: DRF exception context.
    :return: Structured API error response.
    """
    del context

    return build_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=get_error_status_code(exc.code),
    )


def get_drf_error_code(exc: Exception) -> str:
    """Return a stable application code for a DRF exception.

    :param exc: Exception raised by DRF.
    :return: Machine-readable API error code.
    """
    error_codes = {
        exceptions.ValidationError: ErrorCode.VALIDATION_ERROR,
        exceptions.NotAuthenticated: ErrorCode.AUTHENTICATION_FAILED,
        exceptions.AuthenticationFailed: ErrorCode.AUTHENTICATION_FAILED,
        exceptions.PermissionDenied: ErrorCode.PERMISSION_DENIED,
        exceptions.NotFound: ErrorCode.NOT_FOUND,
        exceptions.MethodNotAllowed: ErrorCode.OPERATION_NOT_ALLOWED,
    }

    exc_type = type(exc)
    code = error_codes.get(exc_type)
    if code is not None:
        return code

    logger.warning("unhandled drf exception type: {}", exc_type)

    return "drf_error"


def drf_exception_handler(exc: Exception, context: dict) -> Response:
    """Convert a DRF exception into the common API error response.

    :param exc: Exception raised by DRF.
    :param context: DRF exception context, including request and view.
    :return: Structured API error response.
    """
    response = drf_default_exception_handler(exc, context)

    if response is not None:
        return build_error_response(
            code=get_drf_error_code(exc),
            message=response.data.get("detail", _("An error occurred.")),
            details=response.data,
            status_code=response.status_code,
        )

    request = context.get("request")
    request_id = get_request_id() or "-"

    logger.bind(
        request_id=request_id,
        method=getattr(request, "method", None),
        path=getattr(request, "path", None),
        exception_type=type(exc).__name__,
    ).exception("unhandled api exception")

    return build_error_response(
        code=ErrorCode.SERVER_ERROR,
        message=_("an unexpected error occurred."),
        details={"request_id": request_id},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def api_error_handler(exc: Exception, context: dict) -> Response | None:
    """Dispatch application and DRF exceptions to specialized handlers.

    :param exc: Exception raised while processing the request.
    :param context: DRF exception context.
    :return: Structured response, or ``None`` for unhandled exceptions.
    """
    if isinstance(exc, BaseError):
        return core_error_handler(exc, context)

    return drf_exception_handler(exc, context)
