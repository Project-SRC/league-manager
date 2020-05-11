from datetime import date, datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from src.models.country.country import Country


class Track(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None
    founded: date
    type: str  # [Circuit, Rally, City Circuit, ...] -> TODO: Create Enum for track type -> https://pydantic-docs.helpmanual.io/usage/types/#enums-and-choices
    localtion: Optional[str]  # TODO: Update to use Geolocation
    country: Country
    direction: str  # [Forward, Backwards or Clockwise, Counter-Clockwise] -> TODO: Create Enum for track direction
    length: float  # Length in Km -> Convert to Miles if needed
    number_curves: int
    map: HttpUrl
    record: str  # TODO: Add verification for Time Class create on Time-Operator (see https://github.com/Project-SRC/time-operator)
