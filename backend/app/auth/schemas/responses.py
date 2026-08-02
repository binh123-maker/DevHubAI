from datetime import datetime, timezone
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class StandardAuthResponse(BaseModel, Generic[T]):
    """Standardized Versioned API Response Envelope for Authentication Endpoints."""

    version: str = Field(default="v1", description="API version identifier.")
    success: bool = Field(..., description="Success flag boolean.")
    code: str = Field(default="AUTH_SUCCESS", description="Application error or status code.")
    message: str = Field(..., description="User-facing or diagnostic status message.")
    data: T | None = Field(default=None, description="Payload data returned by endpoint.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp.",
    )
    request_id: str | None = Field(default=None, description="Traceable correlation request ID.")
