from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

# Typing for list of Objects from various classes
Records = list[UUID]

# Typing for prizes: List of dictionaries with position, prize
Prize = list[dict[int, str]]


class League(BaseModel):
    id: UUID | None = None
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    ended_at: datetime | None = None
    races: Records
    teams: Records
    drivers: Records
    points: list[int]  # TODO: Create a class have different styles of pointing
    doubled_points: bool = False
    prize: Prize | None = None
