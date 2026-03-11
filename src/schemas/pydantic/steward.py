from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateSteward(BaseModel):
    """Schema for creating a new steward."""

    user_id: UUID


class UpdateSteward(BaseModel):
    """Schema for updating a steward."""

    active: bool | None = None


class StewardResponse(BaseModel):
    """Schema for steward responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    active: bool = True
    deactivated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
