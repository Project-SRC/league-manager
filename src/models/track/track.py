from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from uuid import UUID
from src.utils.utils import validated_string_time

# CONSTANTS
VALID_TIME_REGEX = "([0-9]+)?(\\:)?([0-9]{2})?(\\:)?([0-9]{2})\\.([0-9]{3})"


class TrackTypeEnum(str, Enum):
    circuit = "Circuit"
    rally = "Rally"
    city_circuit = "City Circuit"
    rally_cross = "Rally Cross"
    off_road = "Off Road"


class TrackDirection(str, Enum):
    normal = "Normal"
    reversed = "Reversed"


class Track(BaseModel):
    id: Optional[UUID]
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    deleted_at: Optional[datetime] = None
    founded: date
    type: TrackTypeEnum  # [Circuit, Rally, City Circuit, ...]
    localtion: Optional[str]  # TODO: Update to use Geolocation
    country: UUID
    direction: TrackDirection
    length: float  # Length in Km -> Convert to Miles if needed
    number_curves: int
    map: Optional[HttpUrl]
    record: Optional[str] = Field(None, regex=VALID_TIME_REGEX, description="Expected time format: HH:MM:SSS.mmm")


# REF: Create Enum for track type -> https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
