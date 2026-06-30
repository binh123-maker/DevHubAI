from uuid import UUID

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    role: str
    full_name: str
    avatar_url: str | None = None
    gender: str = "prefer_not_to_say"

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    avatar_url: str | None = None
    gender: str | None = None
