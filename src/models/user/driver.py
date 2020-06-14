from datetime import date, datetime
from src.models.user.user import User
from typing import Optional
from uuid import UUID

class Driver(User):
    id: UUID
    created_at: datetime
    updated_at: datetime
    current_team: Optional[UUID] = None
    country: UUID
    total_podiums: int = 0
    total_points: int = 0
    total_races: int = 0
    championships_won: int = 0
    birth_date: date
    birth_place: Optional[str]  # TODO: Update to use Geolocation
    number: str
    active: bool = None
