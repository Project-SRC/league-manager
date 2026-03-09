from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

# CONSTANTS
VALID_TIME_REGEX = "([0-9]+)?(\\:)?([0-9]{2})?(\\:)?([0-9]{2})\\.([0-9]{3})"


class TrackTypeEnum(StrEnum):
    circuit = "Circuit"
    rally = "Rally"
    city_circuit = "City Circuit"
    rally_cross = "Rally Cross"
    off_road = "Off Road"


class TrackDirection(StrEnum):
    normal = "Normal"
    reversed = "Reversed"


# REF: Create Enum for track type -> https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
class Track(BaseModel):
    id: UUID | None = None
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: datetime | None = None
    founded: date
    type: TrackTypeEnum  # [Circuit, Rally, City Circuit, ...]
    location: str | None = None  # TODO: Update to use Geolocation
    country: UUID
    direction: TrackDirection
    length: float  # Length in Km -> Convert to Miles if needed
    number_curves: int
    map: HttpUrl | None = None
    record: str | None = Field(
        None, pattern=VALID_TIME_REGEX, description="Expected time format: HH:MM:SSS.mmm"
    )
