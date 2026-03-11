from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateManager(BaseModel):
    """Schema for creating a new manager."""

    user_id: UUID


class UpdateManager(BaseModel):
    """Schema for updating a manager."""

    active: bool | None = None


class ManagerResponse(BaseModel):
    """Schema for manager responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    active: bool = True
    deactivated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
