from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID

# Typing for list of Objects from various classes
Records = List[UUID]


class League(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]
    tracks: Records
    teams: Records
    drivers: Records
    points: List[int]  # TODO: Create a class have different styles of pointing
    doubled_points: bool = False
    prize: List[str]

