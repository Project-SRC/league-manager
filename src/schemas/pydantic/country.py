from __future__ import annotations

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.models.track.track import TrackDirection, TrackTypeEnum


class CreateCountry(BaseModel):
    """Schema for creating a new country."""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    abbreviation: Annotated[
        str, Field(min_length=2, max_length=2, description="Alpha-2 country code")
    ]
    flag: HttpUrl


class UpdateCountry(BaseModel):
    """Schema for updating a country."""

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    abbreviation: Annotated[str | None, Field(min_length=2, max_length=2)] = None
    flag: HttpUrl | None = None


class CountryResponse(BaseModel):
    """Schema for country responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    abbreviation: str
    flag: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CreateTrack(BaseModel):
    """Schema for creating a new track."""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    founded: date
    type: TrackTypeEnum
    location: Annotated[str | None, Field(max_length=255)] = None
    country: UUID
    direction: TrackDirection
    length: Annotated[float, Field(gt=0, description="Length in kilometers")]
    number_curves: Annotated[int, Field(ge=0)]
    map: HttpUrl | None = None
    record: Annotated[
        str | None, Field(pattern=r"([0-9]+)?(\:)?([0-9]{2})?(\:)?([0-9]{2})\.([0-9]{3})")
    ] = None


class UpdateTrack(BaseModel):
    """Schema for updating a track."""

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    founded: date | None = None
    type: TrackTypeEnum | None = None
    location: Annotated[str | None, Field(max_length=255)] = None
    country: UUID | None = None
    direction: TrackDirection | None = None
    length: Annotated[float | None, Field(gt=0)] = None
    number_curves: Annotated[int | None, Field(ge=0)] = None
    map: HttpUrl | None = None
    record: str | None = None


class TrackResponse(BaseModel):
    """Schema for track responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    founded: date
    type: TrackTypeEnum
    location: str | None = None
    country: UUID
    direction: TrackDirection
    length: float
    number_curves: int
    map: str | None = None
    record: str | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CreateLeague(BaseModel):
    """Schema for creating a new league."""

    name: Annotated[str, Field(min_length=1, max_length=255)]
    races: list[UUID] = []
    teams: list[UUID] = []
    drivers: list[UUID] = []
    points: Annotated[list[int], Field(min_length=1)]
    doubled_points: bool = False


class UpdateLeague(BaseModel):
    """Schema for updating a league."""

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    races: list[UUID] | None = None
    teams: list[UUID] | None = None
    drivers: list[UUID] | None = None
    points: list[int] | None = None
    doubled_points: bool | None = None
    ended_at: datetime | None = None


class LeagueResponse(BaseModel):
    """Schema for league responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    races: list[UUID]
    teams: list[UUID]
    drivers: list[UUID]
    points: list[int]
    doubled_points: bool
    prize: list[dict[int, str]] | None = None
    created_at: datetime
    updated_at: datetime
    ended_at: datetime | None = None
