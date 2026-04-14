from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserProfileBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    father_name: str | None = Field(default=None, max_length=100)
    bio: str | None = None
    avatar_media_id: UUID | None = None
    metadata: dict = Field(default_factory=dict)


class UserCreateRequest(UserProfileBase):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    roles: list[str] = Field(default_factory=list)
    is_active: bool = True


class UserProfileResponse(UserProfileBase):
    pass


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    roles: list[str]
    profile: UserProfileResponse
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int
