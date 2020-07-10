from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID


class Team(BaseModel):
    id: Optional[UUID]
    name: str
    base: Optional[str]  # TODO: Update to use Geolocation
    founded: date
    team_chief: UUID
    logo: Optional[HttpUrl]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
