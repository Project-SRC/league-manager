from datetime import date, datetime
from uuid import UUID

from src.models.user.user import User


class Driver(User):
    id: UUID | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    current_team: UUID | None = None
    country: UUID
    total_podiums: int = 0
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
    birth_date: date
    birth_place: str | None = None  # TODO: Update to use Geolocation
    number: str
    active: bool = True
