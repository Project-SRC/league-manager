from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateParticipation(BaseModel):
    """Schema for creating a new participation."""

    race_id: UUID
    driver_id: UUID
    position: Annotated[int | None, Field(ge=1, le=50)] = None
    points: Annotated[int, Field(ge=0)] = 0


class UpdateParticipation(BaseModel):
    """Schema for updating a participation."""

    race_id: UUID | None = None
    driver_id: UUID | None = None
    position: Annotated[int | None, Field(ge=1, le=50)] = None
    points: Annotated[int | None, Field(ge=0)] = None


class ParticipationResponse(BaseModel):
    """Schema for participation responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    race_id: UUID | None = None
    driver_id: UUID | None = None
    position: int | None = None
    points: int = 0
    created_at: datetime
    updated_at: datetime
