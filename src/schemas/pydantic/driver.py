from __future__ import annotations

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateDriver(BaseModel):
    """Schema for creating a new driver."""

    user_id: UUID
    country_id: UUID | None = None
    current_team: UUID | None = None
    number: Annotated[str, Field(min_length=1, max_length=10)]
    birth_date: date | None = None
    birth_place: Annotated[str | None, Field(max_length=255)] = None


class UpdateDriver(BaseModel):
    """Schema for updating a driver."""

    country_id: UUID | None = None
    current_team: UUID | None = None
    number: Annotated[str | None, Field(min_length=1, max_length=10)] = None
    birth_date: date | None = None
    birth_place: Annotated[str | None, Field(max_length=255)] = None
    active: bool | None = None


class DriverResponse(BaseModel):
    """Schema for driver responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    country_id: UUID | None = None
    current_team: UUID | None = None
    total_podiums: int = 0
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
    birth_date: date | None = None
    birth_place: str | None = None
    number: str
    active: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
