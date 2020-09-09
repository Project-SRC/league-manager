from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID

# Typing for list of Objects from various classes
Records = List[UUID]

# Typing for prizes: List of dictionaries with position, prize
Prize = List[Dict[int, str]]


class League(BaseModel):
    id: Optional[UUID]
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    ended_at: Optional[datetime] = None
    races: Records
    teams: Records
    drivers: Records
    points: List[int]  # TODO: Create a class have different styles of pointing
    doubled_points: bool = False
    prize: Optional[Prize] = None
