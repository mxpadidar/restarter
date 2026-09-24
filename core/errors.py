"""This module defines custom exception classes for the application."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Enumeration of error codes for structured API error responses."""

    SERVER_ERROR = "server_error"
    CONFLICT = "conflict"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    OPERATION_NOT_ALLOWED = "operation_not_allowed"


class BaseError(Exception):
    """Base class for application-level API errors."""

    code = ErrorCode.SERVER_ERROR

    def __init__(self, message: str, **extra_detail) -> None:
        super().__init__(message)
        self.message = message
        self.details = extra_detail


class ServerError(BaseError):
    """Raised when an unexpected server-side error occurs."""

    code = ErrorCode.SERVER_ERROR


class ConflictError(BaseError):
    """Raised when an operation conflicts with the current resource state."""

    code = ErrorCode.CONFLICT


class ValidationError(BaseError):
    """Raised when input data fails application-level validation."""

    code = ErrorCode.VALIDATION_ERROR


class AuthenticationError(BaseError):
    """Raised when authentication credentials are missing or invalid."""

    code = ErrorCode.AUTHENTICATION_FAILED


class PermissionDeniedError(BaseError):
    """Raised when the authenticated user cannot perform an operation."""

    code = ErrorCode.PERMISSION_DENIED


class NotFoundError(BaseError):
    """Raised when a requested resource does not exist."""

    code = ErrorCode.NOT_FOUND


class OperationNotAllowedError(BaseError):
    """Raised when an operation is not allowed on the resource."""

    code = ErrorCode.OPERATION_NOT_ALLOWED
