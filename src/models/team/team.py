from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class Team(BaseModel):
    id: UUID | None = None
    name: str
    location: str | None = None  # TODO: Update to use Geolocation
    founded: date
    team_chief: UUID
    logo: HttpUrl | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
