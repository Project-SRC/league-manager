from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Race(BaseModel):
    # TODO: Finalize class
    id: UUID
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None
    track: UUID
    number_laps: Optional[int]
    race_time: Optional[str]
    driver_max: int # Max number of drivers in the Race

class GranTurismoRace(Race):
    pass