from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID

# Typing for list of Objects from various classes
Records = List[UUID]


class League(BaseModel):
    id: Optional[UUID]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    ended_at: Optional[datetime] = None
    tracks: Records
    teams: Records
    drivers: Records
    points: List[int]  # TODO: Create a class have different styles of pointing
    doubled_points: bool = False
    prize: List[str]

