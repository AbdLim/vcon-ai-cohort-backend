from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    status: str = Field(..., description="Response status: 'success' or 'failed'")
    message: str = Field(..., description="Status message")
    data: Optional[T] = Field(default=None, description="Response data")
    error: Optional[dict[str, Any]] = Field(default=None, description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {},
                "error": None,
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """Helper for creating success responses"""

    @staticmethod
    def create(message: str, data: Optional[T] = None) -> APIResponse[T]:
        return APIResponse(status="success", message=message, data=data, error=None)


class ErrorResponse(BaseModel):
    """Helper for creating error responses"""

    @staticmethod
    def create(message: str, error: Optional[dict[str, Any]] = None) -> APIResponse:
        return APIResponse(status="failed", message=message, data=None, error=error)
