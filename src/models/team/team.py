from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID


class Team(BaseModel):
    id: Optional[UUID] = None
    name: str
    base: Optional[str] = None  # TODO: Update to use Geolocation
    founded: date
    team_chief: UUID
    logo: Optional[HttpUrl] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
