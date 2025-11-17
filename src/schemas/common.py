"""
Common Pydantic schemas used across the API.
Includes pagination, error responses, and other shared schemas.
"""
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""

    limit: int
    offset: int
    total: int


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    Wraps a list of items with pagination metadata.

    Usage:
        PaginatedResponse[TransactionResponse]
        PaginatedResponse[AccountResponse]
    """

    data: List[T]
    pagination: PaginationMetadata


class ErrorDetail(BaseModel):
    """Detailed information about an error."""

    field: Optional[str] = None
    reason: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    All API errors follow this structure for consistency.

    Example:
        {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid transaction amount",
                "details": {
                    "field": "amount",
                    "reason": "must be positive"
                }
            }
        }
    """

    error: dict[str, Any]  # Contains: code, message, details (optional)
