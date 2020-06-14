from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Race(BaseModel):
    # TODO: Finalize class
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime
    track: UUID
    number_laps: Optional[int]
    race_time: Optional[str]
    driver_max: int # Max number of drivers in the Race

class GranTurismoRace(Race):
    pass