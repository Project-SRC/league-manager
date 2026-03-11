from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateRace(BaseModel):
    """Schema for creating a new race."""

    track_id: UUID | None = None
    date: datetime
    number_laps: Annotated[int | None, Field(ge=1)] = None
    race_time: Annotated[str | None, Field(max_length=50)] = None
    driver_max: Annotated[int, Field(ge=1, le=50)] = 20


class UpdateRace(BaseModel):
    """Schema for updating a race."""

    track_id: UUID | None = None
    date: datetime | None = None
    number_laps: Annotated[int | None, Field(ge=1)] = None
    race_time: Annotated[str | None, Field(max_length=50)] = None
    driver_max: Annotated[int | None, Field(ge=1, le=50)] = None


class RaceResponse(BaseModel):
    """Schema for race responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    track_id: UUID | None = None
    date: datetime
    number_laps: int | None = None
    race_time: str | None = None
    driver_max: int = 20
    created_at: datetime
    updated_at: datetime
