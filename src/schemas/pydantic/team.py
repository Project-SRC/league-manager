from __future__ import annotations

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateTeam(BaseModel):
    """Schema for creating a new team."""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    location: Annotated[str | None, Field(max_length=255)] = None
    founded: date
    team_chief: UUID
    logo: HttpUrl | None = None


class UpdateTeam(BaseModel):
    """Schema for updating a team."""

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    location: Annotated[str | None, Field(max_length=255)] = None
    founded: date | None = None
    team_chief: UUID | None = None
    logo: HttpUrl | None = None
    total_points: int | None = None
    total_races: int | None = None
    championships_won: int | None = None


class TeamResponse(BaseModel):
    """Schema for team responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str | None = None
    founded: date
    team_chief: UUID
    logo: str | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
