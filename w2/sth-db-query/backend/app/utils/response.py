"""
Response models and error handling utilities.

This module provides standardized response formats and error handling
for the API endpoints.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Base API response model."""

    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(cls, message: str = "Success", data: Any = None) -> "APIResponse":
        """Create a successful response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error_code: str = "INTERNAL_ERROR", details: Any = None) -> "APIResponse":
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            error={"code": error_code, "details": details}
        )


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: str
    message: str
    code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Response for validation errors."""

    success: bool = False
    message: str = "Validation failed"
    errors: list[ErrorDetail]

    @classmethod
    def from_validation_errors(cls, validation_errors: Dict[str, Any]) -> "ValidationErrorResponse":
        """Create validation error response from Pydantic validation errors."""
        errors = []
        for field, field_errors in validation_errors.items():
            for error in field_errors:
                errors.append(ErrorDetail(
                    field=field,
                    message=error.get("msg", "Invalid value"),
                    code=error.get("type")
                ))
        return cls(errors=errors)


# HTTP Status Code mappings for common errors
HTTP_STATUS_CODES = {
    "VALIDATION_ERROR": 400,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
}


def get_http_status_code(error_code: str) -> int:
    """Get HTTP status code for error code."""
    return HTTP_STATUS_CODES.get(error_code, 500)
