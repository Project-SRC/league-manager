from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CreateUser(BaseModel):
    """Schema for creating a new user."""

    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")]
    password: Annotated[str, Field(min_length=8, max_length=100)]
    name: Annotated[str, Field(min_length=1, max_length=255)]
    nickname: Annotated[str | None, Field(max_length=100)] = None
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_lowercase(cls, v: str) -> str:
        return v.lower()


class UpdateUser(BaseModel):
    """Schema for updating a user."""

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    nickname: Annotated[str | None, Field(max_length=100)] = None
    email: EmailStr | None = None
    profile_picture: str | None = None
    is_manager: bool | None = None
    is_driver: bool | None = None
    is_steward: bool | None = None
    is_admin: bool | None = None


class UserResponse(BaseModel):
    """Schema for user responses (excludes password)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    name: str
    nickname: str | None = None
    email: str
    profile_picture: str | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    is_manager: bool = False
    is_driver: bool = False
    is_steward: bool = False
    is_admin: bool = False
    manager_id: UUID | None = None
    driver_id: UUID | None = None
    steward_id: UUID | None = None
