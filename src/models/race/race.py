from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class Race(BaseModel):
    # TODO: Finalize class
    id: UUID | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    date: date
    track: UUID
    number_laps: int | None = None
    race_time: str | None = None
    driver_max: int  # Max number of drivers in the Race


class GranTurismoRace(Race):
    # TODO: Future update to integrate with GT Sport
    pass
